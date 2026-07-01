# -*- coding: utf-8 -*-
import os
import sys
import json
import uuid
import time
import threading
import requests
import re
import html
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add api directory to path to import ai_analyzer (fail-safe for local and Vercel)
try:
    from api.ai_analyzer import analyze_business
except ImportError:
    try:
        from ai_analyzer import analyze_business
    except ImportError:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from ai_analyzer import analyze_business

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Resolve writable paths for DB
if os.environ.get("VERCEL"):
    ORDERS_FILE = os.path.join("/tmp", "orders.json")
    CONFIG_FILE = os.path.join("/tmp", "config.json")
else:
    ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")
    CONFIG_FILE = os.path.join(ROOT_DIR, "config.json")

# Default Config
DEFAULT_CONFIG = {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_TELEGRAM_CHAT_ID"
}

def load_config():
    # 1. Environment variables first (Best practice for Vercel)
    env_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    env_chat = os.environ.get("TELEGRAM_CHAT_ID")
    if env_token and env_chat:
        return {"bot_token": env_token, "chat_id": env_chat}

    # 2. Check read-only config.json in root
    root_config = os.path.join(ROOT_DIR, "config.json")
    if os.path.exists(root_config):
        try:
            with open(root_config, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # 3. Check config.json in /tmp or local fallback path
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Write fallback config if not exist and writable
    if not os.environ.get("VERCEL"):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        except Exception:
            pass
            
    return DEFAULT_CONFIG

# Database Helper supporting Local JSON and Vercel KV (Upstash Redis REST)
class DB:
    @staticmethod
    def get_order(order_id):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                res = requests.post(
                    f"{kv_url}/pipeline",
                    json=[["GET", f"order:{order_id}"]],
                    headers=headers,
                    timeout=8
                )
                if res.status_code == 200:
                    results = res.json()
                    if results and results[0] and results[0].get("result"):
                        return json.loads(results[0]["result"])
            except Exception as e:
                print(f"Vercel KV Error (GET order): {e}")
            return None
        else:
            orders = DB._load_local_orders()
            return orders.get(order_id)

    @staticmethod
    def delete_order(order_id):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        # Get order to find brand slug for deletion
        order = DB.get_order(order_id)
        brand_slug = ""
        if order:
            brand_name = order.get("business_name", "")
            brand_slug = DB._slugify(brand_name)

        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                # Build delete pipeline
                del_cmds = [["DEL", f"order:{order_id}"]]
                if brand_slug:
                    del_cmds.append(["DEL", f"order_by_brand:{brand_slug}"])
                requests.post(f"{kv_url}/pipeline", json=del_cmds, headers=headers, timeout=8)
                
                # Remove from ids list
                ids_res = requests.post(f"{kv_url}/pipeline", json=[["GET", "order_ids"]], headers=headers, timeout=8)
                if ids_res.status_code == 200:
                    results = ids_res.json()
                    if results and results[0] and results[0].get("result"):
                        try:
                            ids = json.loads(results[0]["result"])
                            if order_id in ids:
                                ids.remove(order_id)
                                requests.post(f"{kv_url}/pipeline", json=[["SET", "order_ids", json.dumps(ids)]], headers=headers, timeout=8)
                        except Exception:
                            pass
            except Exception as e:
                print(f"Vercel KV Error (DELETE order): {e}")
        else:
            orders = DB._load_local_orders()
            if order_id in orders:
                del orders[order_id]
                DB._save_local_orders(orders)

    @staticmethod
    def get_order_by_brand(brand_name):
        slug = DB._slugify(brand_name)
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                res = requests.post(
                    f"{kv_url}/pipeline",
                    json=[["GET", f"order_by_brand:{slug}"]],
                    headers=headers,
                    timeout=8
                )
                if res.status_code == 200:
                    results = res.json()
                    if results and results[0] and results[0].get("result"):
                        found_id = results[0]["result"]
                        return DB.get_order(found_id)
            except Exception as e:
                print(f"Vercel KV Error (GET order by brand): {e}")
            return None
        else:
            orders = DB._load_local_orders()
            for o_id, order in orders.items():
                if DB._slugify(order.get("business_name", "")) == slug:
                    return order
            return None

    @staticmethod
    def save_order(order_id, order_data):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        brand_slug = DB._slugify(order_data.get("business_name", ""))
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                order_json = json.dumps(order_data, ensure_ascii=False)
                
                # Use Upstash REST pipeline for atomic multi-set
                pipeline_body = [
                    ["SET", f"order:{order_id}", order_json],
                    ["SET", f"order_by_brand:{brand_slug}", order_id]
                ]
                pipe_res = requests.post(
                    f"{kv_url}/pipeline",
                    json=pipeline_body,
                    headers=headers,
                    timeout=10
                )
                print(f"KV pipeline save: {pipe_res.status_code} {pipe_res.text[:200]}")

                # Also update order_ids list
                ids_res = requests.post(f"{kv_url}/pipeline", json=[["GET", "order_ids"]], headers=headers, timeout=8)
                ids = []
                if ids_res.status_code == 200:
                    results = ids_res.json()
                    if results and results[0] and results[0].get("result"):
                        try:
                            ids = json.loads(results[0]["result"])
                        except Exception:
                            ids = []
                if order_id not in ids:
                    ids.append(order_id)
                    requests.post(
                        f"{kv_url}/pipeline",
                        json=[["SET", "order_ids", json.dumps(ids)]],
                        headers=headers,
                        timeout=8
                    )
            except Exception as e:
                print(f"Vercel KV Error (SET order): {e}")
        else:
            orders = DB._load_local_orders()
            orders[order_id] = order_data
            DB._save_local_orders(orders)

    @staticmethod
    def get_next_counter():
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                res = requests.post(
                    f"{kv_url}/pipeline",
                    json=[["INCR", "order_counter"]],
                    headers=headers,
                    timeout=8
                )
                if res.status_code == 200:
                    results = res.json()
                    if results and results[0] and results[0].get("result") is not None:
                        return int(results[0]["result"])
            except Exception as e:
                print(f"Vercel KV Error (INCR order_counter): {e}")
            return random.randint(100, 999)  # fallback
        else:
            orders = DB._load_local_orders()
            counter = len(orders) + 1
            return counter

    @staticmethod
    def save_pending_action(chat_id, action_data):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                # Store with 10min TTL
                requests.post(
                    f"{kv_url}/pipeline",
                    json=[["SET", f"pending_action:{chat_id}", json.dumps(action_data), "EX", 600]],
                    headers=headers,
                    timeout=8
                )
            except Exception as e:
                print(f"Vercel KV Error (save action): {e}")
        else:
            if not hasattr(DB, "_local_actions"):
                DB._local_actions = {}
            DB._local_actions[str(chat_id)] = action_data

    @staticmethod
    def get_pending_action(chat_id):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                res = requests.post(
                    f"{kv_url}/pipeline",
                    json=[["GET", f"pending_action:{chat_id}"]],
                    headers=headers,
                    timeout=8
                )
                if res.status_code == 200:
                    results = res.json()
                    if results and results[0] and results[0].get("result"):
                        return json.loads(results[0]["result"])
            except Exception as e:
                print(f"Vercel KV Error (get action): {e}")
            return None
        else:
            if hasattr(DB, "_local_actions"):
                return DB._local_actions.get(str(chat_id))
            return None

    @staticmethod
    def delete_pending_action(chat_id):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {
                    "Authorization": f"Bearer {kv_token}",
                    "Content-Type": "application/json"
                }
                requests.post(
                    f"{kv_url}/pipeline",
                    json=[["DEL", f"pending_action:{chat_id}"]],
                    headers=headers,
                    timeout=8
                )
            except Exception as e:
                print(f"Vercel KV Error (delete action): {e}")
        else:
            if hasattr(DB, "_local_actions") and str(chat_id) in DB._local_actions:
                del DB._local_actions[str(chat_id)]

    @staticmethod
    def _load_local_orders():
        if not os.path.exists(ORDERS_FILE):
            return {}
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_local_orders(orders):
        try:
            with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(orders, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving local orders: {e}")

    @staticmethod
    def _slugify(text):
        # Slugify function supporting Arabic and English chars
        text = text.lower().strip()
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"[^\w\-]", "", text)
        return text[:20]

# Static Routes (Only for local dev)
@app.route("/")
def serve_root():
    return send_from_directory(ROOT_DIR, "index.html")

ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.json'}

@app.route("/<path:path>")
def serve_static(path):
    safe_path = os.path.normpath(path)
    if safe_path.startswith("..") or safe_path.startswith("/"):
        return jsonify({"ok": False, "error": "Access denied"}), 403
        
    ext = os.path.splitext(safe_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"ok": False, "error": "File type not allowed"}), 403
        
    return send_from_directory(ROOT_DIR, safe_path)

@app.route("/api/config", methods=["GET"])
def get_config_api():
    config = load_config()
    masked_token = config.get("bot_token", "")
    if masked_token and masked_token != "YOUR_TELEGRAM_BOT_TOKEN":
        if len(masked_token) > 10:
            masked_token = masked_token[:6] + "..." + masked_token[-4:]
    kv_ok = bool(os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL"))
    return jsonify({
        "bot_token_configured": config.get("bot_token") != "YOUR_TELEGRAM_BOT_TOKEN",
        "chat_id_configured": config.get("chat_id") != "YOUR_TELEGRAM_CHAT_ID",
        "bot_token_masked": masked_token,
        "chat_id": config.get("chat_id"),
        "database_type": "Vercel KV (Upstash)" if kv_ok else "Local JSON File",
        "kv_connected": kv_ok
    })

@app.route("/api/config", methods=["POST"])
def update_config_api():
    if os.environ.get("VERCEL"):
        return jsonify({"ok": False, "error": "Configuration updates are locked on Vercel. Use Environment Variables."}), 400
        
    data = request.json or {}
    config = load_config()
    if "bot_token" in data:
        config["bot_token"] = data["bot_token"]
    if "chat_id" in data:
        config["chat_id"] = data["chat_id"]
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return jsonify({"ok": True, "message": "Configuration updated successfully"})

@app.route("/api/setup-webhook", methods=["GET", "POST"])
def setup_webhook_api():
    """Call this endpoint after deploying a new bot token to register the Telegram webhook."""
    host = request.headers.get("Host", "")
    scheme = request.headers.get("X-Forwarded-Proto", "https")
    webhook_url = f"{scheme}://{host}/api/telegram-webhook"
    config = load_config()
    token = config.get("bot_token", "")
    
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
        return jsonify({"ok": False, "error": "Bot token not configured. Set TELEGRAM_BOT_TOKEN env variable."}), 400
    
    try:
        tg_url = f"https://api.telegram.org/bot{token}/setWebhook"
        res = requests.post(
            tg_url,
            json={"url": webhook_url, "allowed_updates": ["message", "callback_query"]},
            timeout=10
        )
        res_data = res.json()
        return jsonify({
            "ok": res_data.get("ok"),
            "description": res_data.get("description", ""),
            "webhook_url": webhook_url,
            "telegram_response": res_data
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/submit-order", methods=["POST"])
def submit_order():
    data = request.json or {}
    business_name = data.get("business_name", "").strip()
    business_type = data.get("business_type", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    socials = data.get("socials", {})
    answers = data.get("answers", [])
    
    # Custom additional details
    project_description = data.get("project_description", "").strip()
    budget_range = data.get("budget_range", "").strip()
    target_audience = data.get("target_audience", "").strip()
    competitors = data.get("competitors", "").strip()
    preferred_colors = data.get("preferred_colors", "").strip()
    has_existing_website = data.get("has_existing_website", False)
    existing_website_url = data.get("existing_website_url", "").strip()

    if not business_name or not phone:
        return jsonify({"ok": False, "error": "Business Name and Phone Number are required"}), 400

    # Egyptian Phone validation
    cleaned_phone = re.sub(r"\s+", "", phone)
    is_egyptian = False
    match = re.match(r"^(\+?2?01[0125]\d{8})$|^(\+?2?1[0125]\d{8})$", cleaned_phone)
    if match:
        is_egyptian = True
        
    if not is_egyptian:
        return jsonify({"ok": False, "error": "Invalid Egyptian phone number. Please enter a valid number (e.g. 010xxxxxxxx)"}), 400

    # 1. Build logical Order ID
    counter = DB.get_next_counter()
    padded_counter = f"{counter:04d}"
    last4_phone = phone[-4:]
    rand_digits = f"{random.randint(1000, 9999)}"
    brand_slug = DB._slugify(business_name)
    order_id = f"{padded_counter}-{last4_phone}-{rand_digits}-{brand_slug}"

    # Run AI Analysis
    analysis = analyze_business(
        business_name, business_type, phone, email, socials, answers,
        project_description=project_description,
        budget_range=budget_range,
        target_audience=target_audience,
        competitors=competitors,
        preferred_colors=preferred_colors,
        has_existing_website=has_existing_website,
        existing_website_url=existing_website_url
    )
    
    order = {
        "id": order_id,
        "business_name": business_name,
        "business_type": business_type,
        "phone": phone,
        "email": email,
        "socials": socials,
        "answers": answers,
        "status": "pending",  # pending, approved, rejected, suspended
        "payment_status": "unpaid", # unpaid, paid
        "cost": "لم تحدد بعد",
        "developer": "لم يحدد بعد",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "analysis": analysis,
        # Additional Form Fields
        "project_description": project_description,
        "budget_range": budget_range,
        "target_audience": target_audience,
        "competitors": competitors,
        "preferred_colors": preferred_colors,
        "has_existing_website": has_existing_website,
        "existing_website_url": existing_website_url,
        "user_chat_id": None
    }

    # Save permanently to database
    DB.save_order(order_id, order)

    # Set webhook dynamically on Vercel
    host = request.headers.get("Host")
    if host and "127.0.0.1" not in host and "localhost" not in host:
        scheme = request.headers.get("X-Forwarded-Proto", "https")
        webhook_url = f"{scheme}://{host}/api/telegram-webhook"
        set_telegram_webhook(webhook_url)

    # Send Telegram notification
    send_telegram_notification(order)

    return jsonify({"ok": True, "order_id": order_id})

@app.route("/api/order/<order_id>", methods=["GET"])
def get_order(order_id):
    order = DB.get_order(order_id)
    if not order:
        return jsonify({"ok": False, "error": "Order not found"}), 404
    return jsonify({"ok": True, "order": order})

@app.route("/api/order/<order_id>/update-status", methods=["POST"])
def update_order_status_api(order_id):
    data = request.json or {}
    status = data.get("status", "").lower()
    if status not in ["pending", "approved", "rejected", "suspended"]:
        return jsonify({"ok": False, "error": "Invalid status"}), 400

    order = DB.get_order(order_id)
    if not order:
        return jsonify({"ok": False, "error": "Order not found"}), 404

    order["status"] = status
    DB.save_order(order_id, order)
    return jsonify({"ok": True, "message": f"Status updated to {status}"})

@app.route("/api/order/<order_id>", methods=["DELETE"])
def delete_order_api(order_id):
    order = DB.get_order(order_id)
    if not order:
        return jsonify({"ok": False, "error": "Order not found"}), 404
    DB.delete_order(order_id)
    return jsonify({"ok": True, "message": "Order deleted permanently"})

# Telegram Webhook Endpoint
@app.route("/api/telegram-webhook", methods=["POST"])
def telegram_webhook():
    update = request.json or {}
    config = load_config()
    token = config.get("bot_token")
    
    if "callback_query" in update:
        cb = update["callback_query"]
        cb_id = cb["id"]
        cb_data = cb.get("data", "")
        msg = cb.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        msg_id = msg.get("message_id")
        
        process_callback_query(token, cb_id, cb_data, chat_id, msg_id, msg.get("text", ""))
    elif "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "").strip()
        photo = msg.get("photo")
        
        process_message_update(token, chat_id, text, photo, msg.get("message_id"))

    return jsonify({"ok": True})

def set_telegram_webhook(url):
    config = load_config()
    token = config.get("bot_token")
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
        return
        
    set_url = f"https://api.telegram.org/bot{token}/setWebhook"
    try:
        res = requests.post(set_url, json={"url": url}, timeout=5)
        if res.ok:
            print(f"Telegram Webhook successfully set to: {url}")
    except Exception as e:
        print(f"Error setting Telegram Webhook: {e}")

def send_telegram_notification(order):
    config = load_config()
    token = config.get("bot_token")
    chat_id = config.get("chat_id")

    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN" or not chat_id or chat_id == "YOUR_TELEGRAM_CHAT_ID":
        print("Telegram bot not configured. Skipping notification.")
        return

    order_id = order["id"]
    name = html.escape(str(order["business_name"]))
    biz_type = html.escape(str(order["business_type"]))
    phone = html.escape(str(order["phone"]))
    email = html.escape(str(order["email"] or "N/A"))
    
    inst = html.escape(str(order["socials"].get("instagram", "N/A")))
    tik = html.escape(str(order["socials"].get("tiktok", "N/A")))
    fb = html.escape(str(order["socials"].get("facebook", "N/A")))
    
    p_desc = html.escape(str(order.get("project_description", "لا يوجد")))
    budget = html.escape(str(order.get("budget_range", "غير محدد")))
    audience = html.escape(str(order.get("target_audience", "غير محدد")))
    comps = html.escape(str(order.get("competitors", "لا يوجد")))
    colors = html.escape(str(order.get("preferred_colors", "غير محدد")))
    
    cost = html.escape(str(order.get("cost", "لم تحدد بعد")))
    dev = html.escape(str(order.get("developer", "لم يحدد بعد")))
    pay_status = "✅ تم الدفع" if order.get("payment_status") == "paid" else "❌ لم يتم الدفع"

    msg = f"<b>📊 طلب تحليل نشاط تجاري جديد</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🆔 <b>رقم الطلب:</b> <code>{order_id}</code>\n"
    msg += f"🏢 <b>اسم النشاط:</b> {name}\n"
    msg += f"🏷️ <b>النوع:</b> {biz_type}\n"
    msg += f"📞 <b>رقم الهاتف:</b> {phone}\n"
    msg += f"📧 <b>البريد:</b> {email}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"📝 <b>وصف المشروع:</b>\n{p_desc}\n"
    msg += f"💰 <b>الميزانية:</b> {budget}\n"
    msg += f"👥 <b>الجمهور المستهدف:</b> {audience}\n"
    msg += f"🏁 <b>المنافسون:</b> {comps}\n"
    msg += f"🎨 <b>الألوان المفضلة:</b> {colors}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🌐 <b>التواصل الاجتماعي:</b>\n"
    msg += f"  • إنستجرام: {inst}\n"
    msg += f"  • تيك توك: {tik}\n"
    msg += f"  • فيسبوك: {fb}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 <b>تفاصيل العمل الحالية:</b>\n"
    msg += f"💵 <b>التكلفة:</b> {cost}\n"
    msg += f"👨‍💻 <b>المطور:</b> {dev}\n"
    msg += f"💳 <b>حالة الدفع:</b> {pay_status}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"⚙️ <b>التحكم في حالة الطلب والعمليات:</b>"

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ قبول", "callback_data": f"approve_{order_id}"},
                {"text": "⏳ تعليق", "callback_data": f"suspend_{order_id}"},
                {"text": "❌ رفض", "callback_data": f"reject_{order_id}"}
            ],
            [
                {"text": "💰 تحديد التكلفة", "callback_data": f"setcost_{order_id}"},
                {"text": "👨‍💻 تعيين مطور", "callback_data": f"setdev_{order_id}"}
            ],
            [
                {"text": "🗑️ حذف الطلب نهائياً", "callback_data": f"delete_{order_id}"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

# Telegram Polling (Fallback for local dev)
def telegram_polling():
    offset = 0
    print("Starting Telegram Bot Polling Thread...")
    while True:
        config = load_config()
        token = config.get("bot_token")
        if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
            time.sleep(5)
            continue

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        payload = {"timeout": 3, "offset": offset}
        try:
            res = requests.get(url, params=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        if "callback_query" in update:
                            cb = update["callback_query"]
                            cb_id = cb["id"]
                            cb_data = cb.get("data", "")
                            msg = cb.get("message", {})
                            chat_id = msg.get("chat", {}).get("id")
                            msg_id = msg.get("message_id")
                            
                            process_callback_query(token, cb_id, cb_data, chat_id, msg_id, msg.get("text", ""))
                        elif "message" in update:
                            msg = update["message"]
                            chat_id = msg.get("chat", {}).get("id")
                            text = msg.get("text", "").strip()
                            photo = msg.get("photo")
                            process_message_update(token, chat_id, text, photo, msg.get("message_id"))
        except Exception as e:
            time.sleep(5)
        time.sleep(1)

def process_callback_query(token, cb_id, cb_data, chat_id, msg_id, original_text):
    action = ""
    status = ""
    order_id = ""

    # Check state commands
    if cb_data == "inquiry":
        # Force reply to user
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "من فضلك أرسل رقم الطلب أو اسم البراند للاستعلام عن الحالة:",
            "reply_markup": {"force_reply": True, "selective": True}
        }
        requests.post(url, json=payload)
        DB.save_pending_action(chat_id, {"action": "inquiry"})
        # answer query
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id})
        return
        
    elif cb_data == "payment":
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "من فضلك أرسل رقم الطلب الخاص بك أولاً لتأكيد الدفع:",
            "reply_markup": {"force_reply": True, "selective": True}
        }
        requests.post(url, json=payload)
        DB.save_pending_action(chat_id, {"action": "payment_id"})
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id})
        return

    # Admin actions on payments
    if cb_data.startswith("pay_approve_"):
        order_id = cb_data.replace("pay_approve_", "")
        order = DB.get_order(order_id)
        if order:
            order["payment_status"] = "paid"
            DB.save_order(order_id, order)
            # Notify admin
            requests.post(f"https://api.telegram.org/bot{token}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": f"✅ تم الموافقة على تحويل الدفعة للطلب <code>{order_id}</code> بنجاح وتم تحديث حالة الطلب.",
                "parse_mode": "HTML"
            })
            # Notify user if chat id exists
            user_chat = order.get("user_chat_id")
            if user_chat:
                usr_msg = f"🎉 <b>تم تأكيد استلام الدفع!</b>\n\nتمت الموافقة على إيصال التحويل الخاص بك بنجاح لطلبك <code>{order_id}</code>.\nتم البدء بالعمل وجاري تنفيذ استراتيجيتك الرقمية."
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                    "chat_id": user_chat,
                    "text": usr_msg,
                    "parse_mode": "HTML"
                })
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id})
        return

    elif cb_data.startswith("pay_reject_"):
        order_id = cb_data.replace("pay_reject_", "")
        order = DB.get_order(order_id)
        if order:
            requests.post(f"https://api.telegram.org/bot{token}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": f"❌ تم رفض إيصال التحويل للطلب <code>{order_id}</code>.",
                "parse_mode": "HTML"
            })
            user_chat = order.get("user_chat_id")
            if user_chat:
                usr_msg = f"⚠️ <b>تنبيه بخصوص الدفع!</b>\n\nللأسف تم رفض إيصال التحويل المرسل لطلبك <code>{order_id}</code>.\nيرجى التحقق من عملية التحويل وإرسال صورة واضحة مرة أخرى، أو التواصل مع الدعم."
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                    "chat_id": user_chat,
                    "text": usr_msg,
                    "parse_mode": "HTML"
                })
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id})
        return

    # Admin cost/developer inline updates
    if cb_data.startswith("setcost_"):
        order_id = cb_data.replace("setcost_", "")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"أرسل تكلفة الطلب الإجمالية بالجنيه المصري (مثال: 5000) للطلب:\n<code>{order_id}</code>",
            "parse_mode": "HTML",
            "reply_markup": {"force_reply": True, "selective": True}
        }
        requests.post(url, json=payload)
        DB.save_pending_action(chat_id, {"action": "set_cost", "order_id": order_id, "original_msg_id": msg_id})
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id})
        return

    elif cb_data.startswith("setdev_"):
        order_id = cb_data.replace("setdev_", "")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"أرسل اسم المطور المسؤول عن هذا العمل للطلب:\n<code>{order_id}</code>",
            "parse_mode": "HTML",
            "reply_markup": {"force_reply": True, "selective": True}
        }
        requests.post(url, json=payload)
        DB.save_pending_action(chat_id, {"action": "set_developer", "order_id": order_id, "original_msg_id": msg_id})
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id})
        return

    # Order lifecycle updates
    if cb_data.startswith("approve_"):
        order_id = cb_data.replace("approve_", "")
        action = "تأكيد"
        status = "approved"
    elif cb_data.startswith("reject_"):
        order_id = cb_data.replace("reject_", "")
        action = "رفض"
        status = "rejected"
    elif cb_data.startswith("suspend_"):
        order_id = cb_data.replace("suspend_", "")
        action = "تعليق"
        status = "suspended"
    elif cb_data.startswith("delete_"):
        order_id = cb_data.replace("delete_", "")
        DB.delete_order(order_id)
        # update message
        del_msg = f"🗑️ <b>تم حذف هذا الطلب نهائياً من قاعدة البيانات!</b>\nرقم الطلب: <code>{order_id}</code>"
        requests.post(f"https://api.telegram.org/bot{token}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": msg_id,
            "text": del_msg,
            "parse_mode": "HTML"
        })
        requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "تم حذف الطلب نهائياً"})
        return

    if not order_id:
        return

    order = DB.get_order(order_id)
    if not order:
        url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        requests.post(url, json={"callback_query_id": cb_id, "text": "الطلب غير موجود في النظام أو تم حذفه", "show_alert": True})
        return

    # Update database
    order["status"] = status
    DB.save_order(order_id, order)

    requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": f"تم {action} الطلب بنجاح"})
    update_admin_message(token, chat_id, msg_id, order)

def process_message_update(token, chat_id, text, photo, msg_id):
    pending = DB.get_pending_action(chat_id)
    
    if text == "/start":
        DB.delete_pending_action(chat_id)
        msg_text = "👋 <b>مرحباً بك في بوت خدمة العملاء وتأكيد الطلبات!</b>\n\nمن هنا يمكنك متابعة طلبك ودفع العربون وتأكيد بيانات البراند الخاص بك.\nمن فضلك اختر إحدى الخدمات المتاحة أدناه:"
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "📋 استعلام عن طلب", "callback_data": "inquiry"},
                    {"text": "💳 تأكيد الدفع", "callback_data": "payment"}
                ]
            ]
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
            "chat_id": chat_id,
            "text": msg_text,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        })
        return

    if not pending:
        return

    action = pending.get("action")
    order_id = pending.get("order_id")
    orig_msg_id = pending.get("original_msg_id")

    if action == "set_cost":
        order = DB.get_order(order_id)
        if order:
            order["cost"] = f"{text} ج.م"
            DB.save_order(order_id, order)
            DB.delete_pending_action(chat_id)
            # Acknowledge to admin
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"💵 تم تحديد التكلفة: <b>{text} ج.م</b> للطلب <code>{order_id}</code>" ,
                "parse_mode": "HTML",
                "reply_to_message_id": msg_id
            })
            update_admin_message(token, chat_id, orig_msg_id, order)
            
    elif action == "set_developer":
        order = DB.get_order(order_id)
        if order:
            order["developer"] = text
            DB.save_order(order_id, order)
            DB.delete_pending_action(chat_id)
            # Acknowledge to admin
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👨‍💻 تم تعيين المطور: <b>{text}</b> للطلب <code>{order_id}</code>" ,
                "parse_mode": "HTML",
                "reply_to_message_id": msg_id
            })
            update_admin_message(token, chat_id, orig_msg_id, order)

    elif action == "inquiry":
        # Search by order_id or brand name
        order = DB.get_order(text)
        if not order:
            order = DB.get_order_by_brand(text)
        
        DB.delete_pending_action(chat_id)
        if not order:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ لم نتمكن من العثور على طلب بهذا الرقم أو بهذا الاسم. يرجى التأكد وإعادة المحاولة.",
                "reply_to_message_id": msg_id
            })
            return

        # Save user chat_id to the order so we can send push messages later
        order_id = order["id"]
        order["user_chat_id"] = chat_id
        DB.save_order(order_id, order)

        status_ar = {
            "pending": "⏳ قيد المراجعة والدراسة",
            "approved": "✅ تم تأكيد وقبول طلبك وجاري التنفيذ",
            "rejected": "❌ تم رفض الطلب (يرجى الاتصال بنا)",
            "suspended": "⚠️ معلق مؤقتاً"
        }.get(order.get("status"), order.get("status"))

        pay_status = order.get("payment_status", "unpaid")
        cost = order.get("cost", "لم تحدد بعد")
        dev = order.get("developer", "لم يحدد بعد")
        brand = order.get("business_name", "")

        msg_body = f"<b>📋 تفاصيل الطلب الخاص بك:</b>\n\n"
        msg_body += f"🏢 <b>اسم البراند:</b> {brand}\n"
        msg_body += f"🆔 <b>رقم الطلب:</b> <code>{order_id}</code>\n"
        msg_body += f"🚦 <b>حالة الطلب:</b> {status_ar}\n"
        msg_body += f"👨‍💻 <b>المطور المسؤول:</b> {dev}\n"
        msg_body += f"💵 <b>التكلفة الإجمالية:</b> {cost}\n"
        
        if pay_status == "paid":
            msg_body += f"💳 <b>حالة الدفع:</b> ✅ تم دفع كامل المبلغ / العربون وجاري العمل."
        else:
            msg_body += f"💳 <b>حالة الدفع:</b> ❌ لم يتم دفع العربون بعد.\n\n"
            msg_body += f"💸 <b>طريقة التحويل المعتمدة:</b>\n"
            msg_body += f"يرجى تحويل نصف التكلفة كعربون استلام لبدء العمل على الرقم التالي:\n"
            msg_body += f"<code>01095817701</code> (فودافون كاش)\n"
            msg_body += f"بعد التحويل، يرجى الضغط على زر 'تأكيد الدفع' وإرفاق صورة الإيصال."

        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
            "chat_id": chat_id,
            "text": msg_body,
            "parse_mode": "HTML"
        })

    elif action == "payment_id":
        order = DB.get_order(text)
        if not order:
            order = DB.get_order_by_brand(text)
        
        if not order:
            DB.delete_pending_action(chat_id)
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ لم نتمكن من العثور على طلب بهذا الرقم أو بهذا الاسم. يرجى التأكد وإعادة المحاولة.",
                "reply_to_message_id": msg_id
            })
            return

        order_id = order["id"]
        order["user_chat_id"] = chat_id
        DB.save_order(order_id, order)

        # Prompt for screenshot
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"✅ تم العثور على البراند: <b>{order.get('business_name')}</b>.\n\nيرجى إرسال صورة إيصال التحويل (Screenshot) الآن:",
            "parse_mode": "HTML",
            "reply_markup": {"force_reply": True, "selective": True}
        }
        requests.post(url, json=payload)
        DB.save_pending_action(chat_id, {"action": "payment_photo", "order_id": order_id})

    elif action == "payment_photo":
        if not photo:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ خطأ: يرجى إرسال إيصال الدفع كصورة وليس كملف أو نص.",
                "reply_markup": {"force_reply": True, "selective": True}
            })
            return

        # Largest photo size
        file_id = photo[-1]["file_id"]
        order = DB.get_order(order_id)
        if not order:
            DB.delete_pending_action(chat_id)
            return

        DB.delete_pending_action(chat_id)

        # Notify admin chat
        config = load_config()
        admin_chat_id = config.get("chat_id")
        
        admin_text = f"📬 <b>إيصال تحويل دفعة جديد!</b>\n\n"
        admin_text += f"🏢 <b>البراند:</b> {order.get('business_name')}\n"
        admin_text += f"🆔 <b>رقم الطلب:</b> <code>{order_id}</code>\n"
        admin_text += f"💵 <b>التكلفة:</b> {order.get('cost')}\n"
        admin_text += f"📞 <b>الهاتف:</b> {order.get('phone')}\n\n"
        admin_text += f"يرجى التحقق من عملية التحويل عبر رقم فودافون كاش واتخاذ القرار:"

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ موافقة وتأكيد الدفع", "callback_data": f"pay_approve_{order_id}"},
                    {"text": "❌ رفض الإيصال", "callback_data": f"pay_reject_{order_id}"}
                ]
            ]
        }

        # Send photo to admin
        photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
        res = requests.post(photo_url, json={
            "chat_id": admin_chat_id,
            "photo": file_id,
            "caption": admin_text,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        })

        if res.status_code == 200:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": "👍 <b>تم إرسال إيصال التحويل بنجاح!</b>\n\nجاري مراجعة التحويل وتدقيق العملية من قبل الإدارة وسوف نخطرك هنا فور تأكيد الدفع."
            })
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"❌ عذراً، حدث خطأ أثناء إرسال الصورة للإدارة. يرجى المحاولة لاحقاً."
            })

def update_admin_message(token, chat_id, msg_id, order):
    order_id = order["id"]
    name = html.escape(str(order["business_name"]))
    biz_type = html.escape(str(order["business_type"]))
    phone = html.escape(str(order["phone"]))
    email = html.escape(str(order["email"] or "N/A"))
    
    inst = html.escape(str(order["socials"].get("instagram", "N/A")))
    tik = html.escape(str(order["socials"].get("tiktok", "N/A")))
    fb = html.escape(str(order["socials"].get("facebook", "N/A")))
    
    p_desc = html.escape(str(order.get("project_description", "لا يوجد")))
    budget = html.escape(str(order.get("budget_range", "غير محدد")))
    audience = html.escape(str(order.get("target_audience", "غير محدد")))
    comps = html.escape(str(order.get("competitors", "لا يوجد")))
    colors = html.escape(str(order.get("preferred_colors", "غير محدد")))
    
    cost = html.escape(str(order.get("cost", "لم تحدد بعد")))
    dev = html.escape(str(order.get("developer", "لم يحدد بعد")))
    pay_status = "✅ تم الدفع" if order.get("payment_status") == "paid" else "❌ لم يتم الدفع"
    
    status_emoji = {
        "pending": "⏳ قيد الانتظار",
        "approved": "✅ تم تأكيد الطلب",
        "rejected": "❌ تم رفض الطلب",
        "suspended": "⏳ تم تعليق الطلب"
    }.get(order.get("status"), "Status Updated")

    msg = f"<b>📊 طلب تحليل نشاط تجاري جديد</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🆔 <b>رقم الطلب:</b> <code>{order_id}</code>\n"
    msg += f"🏢 <b>اسم النشاط:</b> {name}\n"
    msg += f"🏷️ <b>النوع:</b> {biz_type}\n"
    msg += f"📞 <b>رقم الهاتف:</b> {phone}\n"
    msg += f"📧 <b>البريد:</b> {email}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"📝 <b>وصف المشروع:</b>\n{p_desc}\n"
    msg += f"💰 <b>الميزانية:</b> {budget}\n"
    msg += f"👥 <b>الجمهور المستهدف:</b> {audience}\n"
    msg += f"🏁 <b>المنافسون:</b> {comps}\n"
    msg += f"🎨 <b>الألوان المفضلة:</b> {colors}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🌐 <b>التواصل الاجتماعي:</b>\n"
    msg += f"  • إنستجرام: {inst}\n"
    msg += f"  • تيك توك: {tik}\n"
    msg += f"  • فيسبوك: {fb}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 <b>تفاصيل العمل الحالية:</b>\n"
    msg += f"💵 <b>التكلفة:</b> {cost}\n"
    msg += f"👨‍💻 <b>المطور:</b> {dev}\n"
    msg += f"💳 <b>حالة الدفع:</b> {pay_status}\n"
    msg += f"🚦 <b>الحالة الحالية:</b> {status_emoji}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"⚙️ <b>التحكم في حالة الطلب والعمليات:</b>"

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ قبول", "callback_data": f"approve_{order_id}"},
                {"text": "⏳ تعليق", "callback_data": f"suspend_{order_id}"},
                {"text": "❌ رفض", "callback_data": f"reject_{order_id}"}
            ],
            [
                {"text": "💰 تحديد التكلفة", "callback_data": f"setcost_{order_id}"},
                {"text": "👨‍💻 تعيين مطور", "callback_data": f"setdev_{order_id}"}
            ],
            [
                {"text": "🗑️ حذف الطلب نهائياً", "callback_data": f"delete_{order_id}"}
            ]
        ]
    }

    edit_url = f"https://api.telegram.org/bot{token}/editMessageText"
    requests.post(edit_url, json={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    })

# Start Telegram Bot Polling Thread as daemon ONLY if NOT on Vercel
if not os.environ.get("VERCEL"):
    polling_thread = threading.Thread(target=telegram_polling, daemon=True)
    polling_thread.start()
else:
    print("Vercel Serverless mode: Polling thread disabled. Webhooks will handle updates.")

if __name__ == "__main__":
    load_config()
    print("\n" + "="*50)
    print("🚀 DIGITAL AGENCY SYSTEM Dev server")
    print("🌐 Visit: http://127.0.0.1:8000")
    print("="*50 + "\n")
    app.run(host="127.0.0.1", port=8000, debug=True)
