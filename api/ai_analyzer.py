# -*- coding: utf-8 -*-
import os
import json
import requests

def analyze_business(name, biz_type, phone, email, socials, answers):
    """
    Advanced AI engine that uses Google Gemini API if GEMINI_API_KEY environment
    variable is provided, otherwise falls back to a high-quality heuristic model.
    Generates bilingual (AR/EN) analysis.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            return analyze_with_gemini(api_key, name, biz_type, phone, email, socials, answers)
        except Exception as e:
            print(f"Gemini API analysis failed, falling back to local model: {e}")
            
    # Fallback to local heuristic model
    return analyze_with_local_heuristics(name, biz_type, phone, email, socials, answers)

def analyze_with_gemini(api_key, name, biz_type, phone, email, socials, answers):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Format answers for prompt
    answers_text = ""
    for idx, ans in enumerate(answers):
        q = ans.get("question", "")
        a = ans.get("answer", "")
        answers_text += f"Q{idx+1}: {q}\nA{idx+1}: {a}\n\n"
        
    prompt = f"""
You are a senior business strategist and AI systems architect with 100 years of experience.
Analyze the following business details and quiz answers:

Business Name: {name}
Business Type: {biz_type}
Phone: {phone}
Email: {email}
Social Media: {json.dumps(socials)}

Quiz Answers:
{answers_text}

Generate a comprehensive business strategy report in JSON format.
The JSON must strictly conform to the following schema:
{{
  "score": number (out of 100),
  "growth_potential": number (percentage),
  "timeline": "timeline string (e.g. 2-3 weeks)",
  "investment": "estimated investment range (e.g. $2,000 - $5,000)",
  "roi": "estimated ROI range (e.g. 3-4x in 6 months)",
  "swot": {{
    "en": {{
      "strengths": ["strength 1", "strength 2", "strength 3"],
      "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
      "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
      "threats": ["threat 1", "threat 2", "threat 3"]
    }},
    "ar": {{
      "strengths": ["نقطة قوة 1", "نقطة قوة 2", "نقطة قوة 3"],
      "weaknesses": ["نقطة ضعف 1", "نقطة ضعف 2", "نقطة ضعف 3"],
      "opportunities": ["فرصة 1", "فرصة 2", "فرصة 3"],
      "threats": ["تهديد 1", "تهديد 2", "تهديد 3"]
    }}
  }},
  "marketing_plan": {{
    "en": ["tactic 1", "tactic 2", "tactic 3"],
    "ar": ["خطة تسويق 1", "خطة تسويق 2", "خطة تسويق 3"]
  }},
  "action_plan": {{
    "en": [
      "Week 1: Step description",
      "Week 2: Step description",
      "Week 3: Step description",
      "Week 4: Step description"
    ],
    "ar": [
      "الأسبوع 1: وصف الخطوة",
      "الأسبوع 2: وصف الخطوة",
      "الأسبوع 3: وصف الخطوة",
      "الأسبوع 4: وصف الخطوة"
    ]
  }},
  "seo_tips": {{
    "en": ["seo tip 1", "seo tip 2", "seo tip 3"],
    "ar": ["نصيحة سيو 1", "نصيحة سيو 2", "نصيحة سيو 3"]
  }},
  "ai_summary": {{
    "en": "Detailed professional analysis summary in English.",
    "ar": "ملخص تحليلي احترافي مفصل باللغة العربية للنشاط التجاري."
  }}
}}

Ensure all Arabic text is grammatically correct and sounds highly professional. Do not wrap the JSON inside markdown ticks. Return ONLY the raw JSON string.
"""

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, json=payload, headers=headers, timeout=20)
    
    if res.status_code == 200:
        res_data = res.json()
        text_content = res_data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Parse output JSON
        analysis = json.loads(text_content.strip())
        
        # Inject business static info
        analysis["business_name"] = name
        analysis["business_type"] = biz_type
        analysis["phone"] = phone
        analysis["email"] = email or "N/A"
        analysis["socials"] = socials
        return analysis
        
    raise Exception(f"Gemini API returned status code {res.status_code}: {res.text}")

def analyze_with_local_heuristics(name, biz_type, phone, email, socials, answers):
    """
    Local heuristic model serving as a reliable fallback.
    """
    # 1. Parse answers
    channels = []
    challenge = ""
    timeline = ""
    stage = ""

    for ans in answers:
        q = ans.get("question", "")
        a = ans.get("answer", "")
        if "customers come" in q or "عملاؤك" in q:
            channels = a if isinstance(a, list) else [a]
        elif "challenge" in q or "تحدٍ" in q:
            challenge = a
        elif "launch" in q or "الإطلاق" in q:
            timeline = a
        elif "stage" in q or "مرحلة" in q:
            stage = a

    # 2. Calculate score and growth potential
    score = 72
    if "Manual Processes" in challenge or "العمليات اليدوية" in challenge:
        score += 6
    if "Outdated Website" in challenge or "موقع قديم" in challenge:
        score -= 4
    if len(channels) >= 3:
        score += 10
    else:
        score += 5
    score = min(max(score, 55), 98)

    growth_potential = 78
    if "Instagram" in channels or "انستغرام" in channels:
        growth_potential += 5
    if "TikTok" in channels or "تيك توك" in channels:
        growth_potential += 7
    if "Google" in channels or "جوجل" in channels:
        growth_potential += 5
    growth_potential = min(max(growth_potential, 65), 98)

    # Normalized type mapping
    type_map = {
        "Restaurant": "Restaurant", "مطعم": "Restaurant",
        "Fashion": "Fashion", "أزياء": "Fashion",
        "Clinic": "Clinic", "عيادة": "Clinic",
        "Corporate": "Corporate", "شركة": "Corporate",
        "Startup": "Startup", "ناشئة": "Startup",
        "Other": "Other", "آخر": "Other"
    }
    normalized_type = type_map.get(biz_type, "Other")

    # SWOT
    swot = get_local_swot(normalized_type)
    
    # Marketing, Action Plan & SEO
    marketing = get_local_marketing_plan(normalized_type)
    action_plan = get_local_action_plan(normalized_type, challenge)
    seo_tips = get_local_seo_tips(normalized_type)
    
    # Estimates
    investment = "$3,000 - $8,000"
    roi = "3-4x in 6 months"
    est_timeline = "2-4 Weeks"
    
    if normalized_type == "Restaurant":
        investment = "$1,500 - $4,000"
        roi = "150% order increase"
        est_timeline = "2-3 Weeks"
    elif normalized_type == "Fashion":
        investment = "$2,500 - $6,000"
        roi = "3x ROAS"
        est_timeline = "3 Weeks"
    elif normalized_type == "Clinic":
        investment = "$2,000 - $5,000"
        roi = "80% reduction in missed bookings"
        est_timeline = "2 Weeks"

    return {
        "business_name": name,
        "business_type": biz_type,
        "phone": phone,
        "email": email or "N/A",
        "socials": socials,
        "score": score,
        "growth_potential": growth_potential,
        "timeline": est_timeline,
        "investment": investment,
        "roi": roi,
        "swot": swot,
        "marketing_plan": marketing,
        "action_plan": action_plan,
        "seo_tips": seo_tips,
        "ai_summary": get_local_ai_summary(name, normalized_type, challenge)
    }

def get_local_swot(biz_type):
    if biz_type == "Restaurant":
        return {
            "en": {
                "strengths": ["High demand for online delivery", "Strong visual appeal for food products", "High customer lifetime value"],
                "weaknesses": ["Dependency on third-party delivery apps (high fees)", "Low margin per item", "Inconsistent customer data collection"],
                "opportunities": ["Create direct-to-consumer ordering system", "Implement automated loyalty rewards", "Hyper-local Google Map ads"],
                "threats": ["Fierce local competition", "Rising ingredient and packaging costs", "Negative online reviews impacting reputation"]
            },
            "ar": {
                "strengths": ["طلب مرتفع على التوصيل عبر الإنترنت", "جاذبية بصرية قوية للمأكولات", "قيمة عمرية عالية للعميل"],
                "weaknesses": ["الاعتماد على تطبيقات التوصيل الخارجية (رسوم مرتفعة)", "هوامش ربح منخفضة للوجبة", "عدم جمع بيانات العملاء بشكل منظم"],
                "opportunities": ["إنشاء منصة طلب مباشرة لتجنب العمولات", "تطبيق برنامج ولاء ومكافآت تلقائي", "إعلانات جوجل المحلية المستهدفة للمنطقة"],
                "threats": ["المنافسة المحلية الشديدة", "ارتفاع تكاليف المكونات والتعبئة", "التقييمات السلبية عبر الإنترنت التي تؤثر على السمعة"]
            }
        }
    elif biz_type == "Fashion":
        return {
            "en": {
                "strengths": ["Highly shareable and visual content", "Global shipping possibilities", "Strong potential for influencer partnerships"],
                "weaknesses": ["High return rates due to sizing issues", "Intense price competition", "High cart abandonment rates"],
                "opportunities": ["Implement an AI size guide on the store", "Launch automated retargeting flows for cart recovery", "Leverage TikTok Shop / Instagram Checkout"],
                "threats": ["Rapidly changing style trends", "Supply chain and inventory delays", "Platform algorithm changes impacting organic reach"]
            },
            "ar": {
                "strengths": ["محتوى مرئي جذاب وسهل المشاركة", "إمكانيات شحن عالمية ومحلية واسعة", "إمكانيات قوية للشراكة مع المؤثرين"],
                "weaknesses": ["معدلات إرجاع عالية بسبب مقاسات الملابس", "منافسة سعرية شديدة جداً", "نسبة عالية لسلات التسوق المتروكة"],
                "opportunities": ["إضافة دليل مقاسات ذكي في المتجر", "إطلاق حملات إعادة استهداف تلقائية للسلات المتروكة", "استغلال البيع المباشر عبر تيك توك وإنستجرام"],
                "threats": ["تغير صيحات الموضة بسرعة كبيرة", "تأخيرات في سلسلة التوريد والمخزون", "تغييرات خوارزميات المنصات التي تؤثر على الوصول المجاني"]
            }
        }
    elif biz_type == "Clinic":
        return {
            "en": {
                "strengths": ["High trust requirement builds strong patient relationships", "High search intent for medical specialties", "Word-of-mouth referral potential"],
                "weaknesses": ["Time-bound services (limited capacity)", "Difficulty in showing patient results due to privacy", "High no-show rates for appointments"],
                "opportunities": ["Automated SMS/WhatsApp booking confirmation and reminders", "Telehealth integrations for remote consults", "SEO content detailing doctor authority"],
                "threats": ["Competitor clinics offering lower consultation fees", "Negative Google reviews", "Strict regulations on medical advertising"]
            },
            "ar": {
                "strengths": ["طلب الثقة العالي يبني علاقات قوية مع المرضى", "معدل بحث مرتفع عن التخصصات الطبية", "إمكانية إحالة قوية عن طريق التوصيات الشخصية"],
                "weaknesses": ["خدمات مرتبطة بالوقت (طاقة استيعابية محدودة)", "صعوبة عرض نتائج المرضى بسبب الخصوصية الطبية", "معدلات غياب عالية للمواعيد دون إلغاء مسبق"],
                "opportunities": ["تفعيل رسائل تأكيد ومواعيد تلقائية عبر واتساب/SMS", "تكامل الاستشارات عن بعد لزيادة الوصول", "تحسين محركات البحث للتركيز على خبرة الطبيب"],
                "threats": ["عيادات منافسة تقدم أسعار كشف أقل", "التقييمات السلبية على خرائط جوجل", "لوائح وقوانين صارمة على الإعلانات الطبية"]
            }
        }
    else:
        return {
            "en": {
                "strengths": ["Unique positioning and agility", "Direct founder-customer communication", "Low initial operating overhead"],
                "weaknesses": ["Limited brand awareness", "Lack of specialized digital marketing expertise", "Tight budget constraints"],
                "opportunities": ["Leverage niche SEO keywords to outrank big players", "Implement automated email marketing sequence", "Build a high-performance landing page targeting 1 primary action"],
                "threats": ["Established competitors with large marketing budgets", "Rapid technological obsolescence", "High customer acquisition costs"]
            },
            "ar": {
                "strengths": ["موقع فريد ومرونة عالية في اتخاذ القرار", "اتصال مباشر بين المؤسس والعميل", "تكاليف تشغيلية أولية منخفضة"],
                "weaknesses": ["وعي محدود بالعلامة التجارية حالياً", "نقص الخبرة المتخصصة في التسويق الرقمي", "قيود ميزانية مشددة في البداية"],
                "opportunities": ["استغلال الكلمات المفتاحية المتخصصة للتفوق على الكبار", "تطبيق سلسلة تسويق تلقائية عبر البريد/واتساب", "بناء صفحة هبوط عالية الأداء تركز على إجراء أساسي واحد"],
                "threats": ["منافسون راسخون بميزانيات تسويقية ضخمة", "التقادم التكنولوجي السريع", "تكلفة عالية لاستحواذ العملاء الجدد"]
            }
        }

def get_local_marketing_plan(biz_type):
    if biz_type == "Restaurant":
        return {
            "en": [
                "Visual Food Content: Post daily high-definition reels of food preparation on Instagram/TikTok.",
                "Local SEO Optimization: Set up Google Business Profile and actively collect reviews to rank in the Google Map Pack.",
                "Influencer Food Tastings: Invite local food bloggers in exchange for social media coverage."
            ],
            "ar": [
                "محتوى طعام مرئي: نشر مقاطع ريلز يومية عالية الدقة لتحضير الطعام على إنستجرام وتيك توك.",
                "تحسين محركات البحث المحلية: إعداد ملف جوجل التجاري وجمع التقييمات للظهور في نتائج خرائط جوجل الأولى.",
                "دعوة مدوني طعام: دعوة صناع المحتوى المهتمين بالطعام لتجربة قائمة الطعام مقابل تغطية على حساباتهم."
            ]
        }
    elif biz_type == "Fashion":
        return {
            "en": [
                "Micro-influencer Campaigns: Seed free products to creators with 5k-20k followers.",
                "Retargeting Ads: Run Meta catalog ads targeting users who added items to cart but did not purchase.",
                "User Generated Content: Run a contest encouraging customers to post photos wearing your brand."
            ],
            "ar": [
                "حملات المؤثرين الصغار: إرسال منتجات مجانية لصناع محتوى الموضة الذين لديهم من 5 إلى 20 ألف متابع.",
                "إعلانات إعادة الاستهداف: تشغيل إعلانات كتالوج ميتا لاستهداف العملاء الذين أضافوا منتجات للسلة ولم يشتروا.",
                "المحتوى من صنع المستخدمين: إطلاق مسابقة تشجع العملاء على نشر صور بمنتجاتك مقابل فرصة لربح قسيمة شراء."
            ]
        }
    elif biz_type == "Clinic":
        return {
            "en": [
                "Educational Video Series: Short Q&A videos with the doctor explaining common myths on TikTok and Instagram.",
                "Google Search Ads: Target high-intent queries like 'best dermatologist near me' or 'cardiologist booking'.",
                "Patient Testimonial Videos: Video stories of patients sharing their successful journey."
            ],
            "ar": [
                "سلسلة فيديوهات تعليمية: فيديوهات قصيرة للطبيب يجيب فيها عن أسئلة شائعة على تيك توك وإنستجرام.",
                "إعلانات بحث جوجل: استهداف الكلمات ذات النية العالية مثل 'أفضل طبيب جلدية بالقرب مني' أو 'حجز طبيب قلب'.",
                "فيديوهات تجارب المرضى: قصص مصورة لمرضى يشاركون رحلة علاجهم الناجحة (بعد أخذ موافقتهم)."
            ]
        }
    else:
        return {
            "en": [
                "Educational Blogging: Answer the top 20 questions your customers ask on Google.",
                "Direct Outreach: Use LinkedIn or cold WhatsApp outreach to target business clients (B2B).",
                "Case Study Funnel: Build a detailed case study page demonstrating how you solved a client's problem."
            ],
            "ar": [
                "التدوين التعليمي: الإجابة على أكثر 20 سؤالاً يسألها عملاؤك على جوجل في مقالات متخصصة.",
                "التواصل المباشر: استخدام لينكد إن أو واتساب للتواصل المباشر مع العملاء من الشركات (B2B).",
                "قمع دراسة الحالة: بناء صفحة دراسة حالة مفصلة توضح كيف قمت بحل مشكلة عميل سابق بالتفصيل."
            ]
        }

def get_local_action_plan(biz_type, challenge):
    return {
        "en": [
            "Week 1: Core Platform Setup - Secure domain and set up high-performance cloud hosting.",
            "Week 2: Conversion Copywriting & Layout Design - Design Shadcn-style user interfaces focused on your primary business objectives.",
            "Week 3: Automation Integration - Connect CRM, automated WhatsApp notifications, and order routing.",
            "Week 4: Launch & Direct Traffic - Run target micro-campaigns on social media to generate initial traction."
        ],
        "ar": [
            "الأسبوع 1: إعداد المنصة الأساسية - حجز النطاق (الدوامين) وإعداد استضافة سحابية عالية الأداء.",
            "الأسبوع 2: كتابة المحتوى الإقناعي والتصميم - تصميم واجهات مستخدم متميزة بأسلوب Shadcn تركز على أهداف العمل الأساسية.",
            "الأسبوع 3: دمج الأتمتة - ربط نظام إدارة العملاء CRM وتنبيهات واتساب التلقائية وتوجيه الطلبات.",
            "الأسبوع 4: الإطلاق وجلب الزوار - تشغيل حملات تسويقية مصغرة ومستهدفة على وسائل التواصل لجلب أول دفعة عملاء."
        ]
    }

def get_local_seo_tips(biz_type):
    return {
        "en": [
            "Core Web Vitals Optimization: Ensure mobile page load time is under 1.5 seconds.",
            "Schema Markup: Implement LocalBusiness or Product structured data schema to get rich snippets on Google.",
            "Keyword-Rich Headers: Structure pages using 1 principal H1 containing the main target keyword, followed by H2s and H3s."
        ],
        "ar": [
            "تحسين مؤشرات أداء الويب الأساسية: التأكد من أن وقت تحميل صفحة الجوال أقل من 1.5 ثانية.",
            "بيانات Schema المنظمة: تطبيق كود سكيما (LocalBusiness أو Product) للحصول على نتائج غنية في جوجل.",
            "عناوين غنية بالكلمات المفتاحية: تنظيم الصفحات باستخدام عنوان رئيسي واحد H1 يحتوي الكلمة المستهدفة، يليه H2 ثم H3."
        ]
    }

def get_local_ai_summary(name, biz_type, challenge):
    return {
        "en": f"AI Strategy Overview for '{name}': As a {biz_type} business, your primary bottleneck is resolved by shifting focus from standard landing pages to an automated high-conversion system. By solving the '{challenge}' challenge, we estimate a direct increase in conversion rate by up to 45% using structured user experience designs.",
        "ar": f"نظرة عامة على استراتيجية الذكاء الاصطناعي لـ '{name}': كنشاط تجاري في مجال ({biz_type})، يتم حل العقبة الرئيسية لعملك عن طريق تحويل التركيز من صفحات الهبوط التقليدية إلى نظام أوتوماتيكي عالي التحويل. من خلال حل تحدي '{challenge}'، نقدر زيادة مباشرة في معدل التحويل تصل إلى 45% باستخدام تصاميم تجربة مستخدم منظمة."
    }
