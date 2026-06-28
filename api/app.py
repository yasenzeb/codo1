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
        
        # If KV URL starts with redis://, convert to REST URL if possible or just use REST vars
        if kv_url and kv_token:
            # Clean protocol if redis:// was passed
            if kv_url.startswith("redis://") or kv_url.startswith("rediss://"):
                # Usually Vercel injects KV_REST_API_URL. If not, log warning.
                pass
            try:
                headers = {"Authorization": f"Bearer {kv_token}"}
                res = requests.get(f"{kv_url}/get/order:{order_id}", headers=headers, timeout=5)
                if res.status_code == 200:
                    val = res.json().get("result")
                    if val:
                        return json.loads(val)
            except Exception as e:
                print(f"Vercel KV Error (GET): {e}")
            return None
        else:
            # Local fallback
            orders = DB._load_local_orders()
            return orders.get(order_id)

    @staticmethod
    def save_order(order_id, order_data):
        kv_url = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
        kv_token = os.environ.get("KV_REST_API_TOKEN")
        
        if kv_url and kv_token:
            try:
                headers = {"Authorization": f"Bearer {kv_token}"}
                # Set order key
                requests.post(f"{kv_url}/set/order:{order_id}", data=json.dumps(order_data), headers=headers, timeout=5)
                
                # Maintain list of order IDs (optional, but good for listing)
                # We can fetch existing list, append, and save
                ids_res = requests.get(f"{kv_url}/get/order_ids", headers=headers, timeout=5)
                ids = []
                if ids_res.status_code == 200:
                    ids_val = ids_res.json().get("result")
                    if ids_val:
                        ids = json.loads(ids_val)
                if order_id not in ids:
                    ids.append(order_id)
                    requests.post(f"{kv_url}/set/order_ids", data=json.dumps(ids), headers=headers, timeout=5)
            except Exception as e:
                print(f"Vercel KV Error (SET): {e}")
        else:
            # Local fallback
            orders = DB._load_local_orders()
            orders[order_id] = order_data
            DB._save_local_orders(orders)

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

# Static Routes (Only for local dev)
@app.route("/")
def serve_root():
    return send_from_directory(ROOT_DIR, "index.html")

ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.json'}

@app.route("/<path:path>")
def serve_static(path):
    # Prevent path traversal vulnerabilities
    safe_path = os.path.normpath(path)
    if safe_path.startswith("..") or safe_path.startswith("/"):
        return jsonify({"ok": False, "error": "Access denied"}), 403
        
    ext = os.path.splitext(safe_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"ok": False, "error": "File type not allowed"}), 403
        
    return send_from_directory(ROOT_DIR, safe_path)

# API Routes
@app.route("/api/config", methods=["GET"])
def get_config_api():
    config = load_config()
    masked_token = config.get("bot_token", "")
    if masked_token and masked_token != "YOUR_TELEGRAM_BOT_TOKEN":
        if len(masked_token) > 10:
            masked_token = masked_token[:6] + "..." + masked_token[-4:]
    return jsonify({
        "bot_token_configured": config.get("bot_token") != "YOUR_TELEGRAM_BOT_TOKEN",
        "chat_id_configured": config.get("chat_id") != "YOUR_TELEGRAM_CHAT_ID",
        "bot_token_masked": masked_token,
        "chat_id": config.get("chat_id"),
        "database_type": "Vercel KV" if (os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")) else "Local JSON"
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

@app.route("/api/submit-order", methods=["POST"])
def submit_order():
    data = request.json or {}
    business_name = data.get("business_name", "").strip()
    business_type = data.get("business_type", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    socials = data.get("socials", {})
    answers = data.get("answers", [])

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

    order_id = str(uuid.uuid4())
    
    # Run AI Analysis
    analysis = analyze_business(business_name, business_type, phone, email, socials, answers)
    
    order = {
        "id": order_id,
        "business_name": business_name,
        "business_type": business_type,
        "phone": phone,
        "email": email,
        "socials": socials,
        "answers": answers,
        "status": "pending",  # pending, approved, rejected, suspended
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "analysis": analysis
    }

    # Save to database
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

# Telegram Webhook Endpoint (For Serverless deployment on Vercel)
@app.route("/api/telegram-webhook", methods=["POST"])
def telegram_webhook():
    update = request.json or {}
    if "callback_query" in update:
        cb = update["callback_query"]
        cb_id = cb["id"]
        cb_data = cb.get("data", "")
        msg = cb.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        msg_id = msg.get("message_id")
        
        config = load_config()
        token = config.get("bot_token")
        
        process_callback_query(token, cb_id, cb_data, chat_id, msg_id, msg.get("text", ""))
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

    msg = f"<b>📊 طلب تحليل نشاط تجاري جديد</b>\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🆔 <b>رقم الطلب:</b> <code>{order_id}</code>\n"
    msg += f"🏢 <b>اسم النشاط:</b> {name}\n"
    msg += f"🏷️ <b>النوع:</b> {biz_type}\n"
    msg += f"📞 <b>رقم الهاتف:</b> {phone}\n"
    msg += f"📧 <b>البريد:</b> {email}\n"
    msg += f"🌐 <b>التواصل الاجتماعي:</b>\n"
    msg += f"  • إنستجرام: {inst}\n"
    msg += f"  • تيك توك: {tik}\n"
    msg += f"  • فيسبوك: {fb}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"⚙️ <b>التحكم في حالة الطلب:</b>"

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ تأكيد الطلب", "callback_data": f"approve_{order_id}"},
                {"text": "❌ رفض الطلب", "callback_data": f"reject_{order_id}"}
            ],
            [
                {"text": "⏳ تعليق الطلب", "callback_data": f"suspend_{order_id}"}
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
        except Exception:
            time.sleep(5)
        time.sleep(1)

def process_callback_query(token, cb_id, cb_data, chat_id, msg_id, original_text):
    action = ""
    status = ""
    order_id = ""

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

    if not order_id:
        return

    order = DB.get_order(order_id)
    if not order:
        url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        requests.post(url, json={"callback_query_id": cb_id, "text": "الطلب غير موجود في النظام", "show_alert": True})
        return

    # Update database
    order["status"] = status
    DB.save_order(order_id, order)

    # Acknowledge callback query
    ans_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    requests.post(ans_url, json={"callback_query_id": cb_id, "text": f"تم {action} الطلب بنجاح"})

    # Update Telegram Message
    status_emoji = {
        "approved": "✅ تم تأكيد الطلب",
        "rejected": "❌ تم رفض الطلب",
        "suspended": "⏳ تم تعليق الطلب"
    }.get(status, "Status Updated")

    updated_msg = original_text.split("⚙️ التحكم في حالة الطلب:")[0]
    updated_msg += f"\n⚙️ <b>الحالة الحالية:</b> {status_emoji}"

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ تأكيد الطلب", "callback_data": f"approve_{order_id}"},
                {"text": "❌ رفض الطلب", "callback_data": f"reject_{order_id}"}
            ],
            [
                {"text": "⏳ تعليق الطلب", "callback_data": f"suspend_{order_id}"}
            ]
        ]
    }

    edit_url = f"https://api.telegram.org/bot{token}/editMessageText"
    requests.post(edit_url, json={
        "chat_id": chat_id,
        "message_id": msg_id,
        "text": updated_msg,
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
