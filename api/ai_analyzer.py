# -*- coding: utf-8 -*-
import os
import json
import requests

def analyze_business(name, biz_type, phone, email, socials, answers, 
                     project_description='', budget_range='', 
                     target_audience='', competitors='',
                     preferred_colors='', has_existing_website=False,
                     existing_website_url=''):
    """
    Advanced AI engine that uses Google Gemini API if GEMINI_API_KEY environment
    variable is provided, otherwise falls back to a high-quality heuristic model.
    Generates bilingual (AR/EN) analysis.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            return analyze_with_gemini(api_key, name, biz_type, phone, email, socials, answers,
                                       project_description, budget_range, target_audience,
                                       competitors, preferred_colors, has_existing_website,
                                       existing_website_url)
        except Exception as e:
            print(f"Gemini API analysis failed, falling back to local model: {e}")
            
    # Fallback to local heuristic model
    return analyze_with_local_heuristics(name, biz_type, phone, email, socials, answers,
                                         project_description, budget_range, target_audience,
                                         competitors, preferred_colors, has_existing_website,
                                         existing_website_url)

def analyze_with_gemini(api_key, name, biz_type, phone, email, socials, answers,
                       project_description, budget_range, target_audience,
                       competitors, preferred_colors, has_existing_website,
                       existing_website_url):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Format answers for prompt
    answers_text = ""
    for idx, ans in enumerate(answers):
        q = ans.get("question", "")
        a = ans.get("answer", "")
        answers_text += f"Q{idx+1}: {q}\nA{idx+1}: {a}\n\n"
        
    prompt = f"""
You are a senior business strategist, marketing expert, and AI systems architect with 100 years of experience.
Analyze the following business details, custom inputs, and quiz answers to produce a premium strategic growth blueprint.

Please simulate searching the web and the Egyptian market to customize this analysis specifically for:
Business Name: {name}
Business Type: {biz_type}
Phone: {phone}
Email: {email}
Social Media: {json.dumps(socials)}
Project Description: {project_description}
Budget Range: {budget_range}
Target Audience: {target_audience}
Competitors: {competitors}
Preferred Colors: {preferred_colors}
Has Existing Website: {has_existing_website} (URL: {existing_website_url})

Quiz Answers:
{answers_text}

Generate a comprehensive business strategy report in JSON format.
The JSON must strictly conform to the following schema:
{{
  "score": number (out of 100, evaluate logically based on details),
  "growth_potential": number (percentage),
  "timeline": "timeline string (e.g. 2-3 weeks)",
  "investment": "estimated investment range (e.g. $2,000 - $5,000)",
  "roi": "estimated ROI range (e.g. 3-4x in 6 months)",
  "market_analysis": {{
    "en": "Detailed realistic market analysis in English specific to Egypt's current market.",
    "ar": "تحليل واقعي ومفصل للسوق باللغة العربية مخصص للسوق المصري الحالي."
  }},
  "competitor_analysis": {{
    "en": "Competitor analysis or positioning strategy based on competitors: {competitors}.",
    "ar": "تحليل المنافسين واستراتيجية التموضع بناءً على المنافسين: {competitors}."
  }},
  "swot": {{
    "en": {{
      "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
      "weaknesses": ["weakness 1", "weakness 2", "weakness 3", "weakness 4"],
      "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3", "opportunity 4"],
      "threats": ["threat 1", "threat 2", "threat 3", "threat 4"]
    }},
    "ar": {{
      "strengths": ["نقطة قوة 1", "نقطة قوة 2", "نقطة قوة 3", "نقطة قوة 4"],
      "weaknesses": ["نقطة ضعف 1", "نقطة ضعف 2", "نقطة ضعف 3", "نقطة ضعف 4"],
      "opportunities": ["فرصة 1", "فرصة 2", "فرصة 3", "فرصة 4"],
      "threats": ["تهديد 1", "تهديد 2", "تهديد 3", "تهديد 4"]
    }}
  }},
  "marketing_plan": {{
    "en": ["Tactic 1 with details", "Tactic 2 with details", "Tactic 3 with details", "Tactic 4 with details", "Tactic 5 with details"],
    "ar": ["تكتيك تسويقي 1 بالتفصيل", "تكتيك تسويقي 2 بالتفصيل", "تكتيك تسويقي 3 بالتفصيل", "تكتيك تسويقي 4 بالتفصيل", "تكتيك تسويقي 5 بالتفصيل"]
  }},
  "action_plan": {{
    "en": [
      "Week 1: Specific core implementation details",
      "Week 2: Specific core implementation details",
      "Week 3: Specific core implementation details",
      "Week 4: Specific core implementation details"
    ],
    "ar": [
      "الأسبوع 1: تفاصيل التنفيذ الأساسية المحددة",
      "الأسبوع 2: تفاصيل التنفيذ الأساسية المحددة",
      "الأسبوع 3: تفاصيل التنفيذ الأساسية المحددة",
      "الأسبوع 4: تفاصيل التنفيذ الأساسية المحددة"
    ]
  }},
  "seo_tips": {{
    "en": ["SEO Tip 1 specific to their industry", "SEO Tip 2 specific to their industry", "SEO Tip 3 specific to their industry", "SEO Tip 4"],
    "ar": ["نصيحة سيو 1 مخصصة لمجالهم", "نصيحة سيو 2 مخصصة لمجالهم", "نصيحة سيو 3 مخصصة لمجالهم", "نصيحة سيو 4"]
  }},
  "ai_summary": {{
    "en": "Comprehensive AI summary of the business strategy in English.",
    "ar": "ملخص تحليلي استراتيجي شامل باللغة العربية للنشاط التجاري."
  }},
  "recommended_tech_stack": {{
    "en": ["Tech 1 (e.g. Next.js, React, Node.js)", "Tech 2", "Tech 3"],
    "ar": ["التقنية 1 (مثال: Next.js, React)", "التقنية 2", "التقنية 3"]
  }},
  "target_audience_analysis": {{
    "en": "Detailed profile of the ideal target customer base in English.",
    "ar": "تحليل دقيق وتفصيلي لفئات الجمهور المستهدف وعملائهم المثاليين بالعربية."
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

def analyze_with_local_heuristics(name, biz_type, phone, email, socials, answers,
                                 project_description, budget_range, target_audience,
                                 competitors, preferred_colors, has_existing_website,
                                 existing_website_url):
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
    score = 75
    if "Manual Processes" in challenge or "العمليات اليدوية" in challenge:
        score += 5
    if "Outdated Website" in challenge or "موقع قديم" in challenge:
        score -= 5
    if len(channels) >= 3:
        score += 8
    else:
        score += 4
    if project_description:
        score += 3
    score = min(max(score, 50), 98)

    growth_potential = 75
    if "Instagram" in channels or "انستغرام" in channels:
        growth_potential += 6
    if "TikTok" in channels or "تيك توك" in channels:
        growth_potential += 8
    if "Google" in channels or "جوجل" in channels:
        growth_potential += 5
    growth_potential = min(max(growth_potential, 60), 98)

    # Normalized type mapping
    type_map = {
        "Restaurant": "Restaurant", "مطعم": "Restaurant",
        "Fashion": "Fashion", "أزياء": "Fashion",
        "Clinic": "Clinic", "عيادة": "Clinic",
        "Corporate": "Corporate", "شركة": "Corporate",
        "Startup": "Startup", "ناشئة": "Startup",
        "E-commerce": "E-commerce", "تجارة إلكترونية": "E-commerce",
        "Education": "Education", "تعليم": "Education",
        "Real Estate": "Real Estate", "عقارات": "Real Estate",
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
    investment = "$2,500 - $6,000"
    roi = "3-4x in 6 months"
    est_timeline = "2-4 Weeks"
    
    if normalized_type == "Restaurant":
        investment = "$1,500 - $3,500"
        roi = "150% order increase"
        est_timeline = "2 Weeks"
    elif normalized_type == "Fashion":
        investment = "$2,000 - $5,000"
        roi = "3x ROAS"
        est_timeline = "3 Weeks"
    elif normalized_type == "Clinic":
        investment = "$2,000 - $4,500"
        roi = "80% booking rate increase"
        est_timeline = "2 Weeks"
    elif normalized_type == "E-commerce":
        investment = "$3,000 - $7,000"
        roi = "4x average ROI"
        est_timeline = "3 Weeks"

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
        "market_analysis": {
            "en": f"Market dynamics for {normalized_type} are highly digital. Consumers in Egypt rely heavily on online reviews, social proof, and mobile accessibility to interact with brands.",
            "ar": f"تتميز ديناميكيات السوق لقطاع ({biz_type}) بالاعتماد الرقمي العالي. يعتمد المستهلكون في مصر بشكل كبير على المراجعات عبر الإنترنت، والقبول الاجتماعي، وسهولة الاستخدام عبر الهاتف للتفاعل مع العلامات التجارية."
        },
        "competitor_analysis": {
            "en": f"Competitors in the {normalized_type} sector are leveraging Facebook Ads and WhatsApp business automation. Differentiation requires a lightning-fast custom web app and a loyalty CRM.",
            "ar": f"يعتمد المنافسون في قطاع ({biz_type}) على إعلانات فيسبوك وأتمتة واتساب للأعمال. يتطلب التميز بناء تطبيق ويب مخصص فائق السرعة مع نظام إدارة علاقات العملاء وبرامج الولاء."
        },
        "swot": swot,
        "marketing_plan": marketing,
        "action_plan": action_plan,
        "seo_tips": seo_tips,
        "ai_summary": get_local_ai_summary(name, normalized_type, challenge),
        "recommended_tech_stack": {
            "en": ["Next.js (React)", "Node.js / Python API", "Tailwind CSS", "Vercel / Upstash DB"],
            "ar": ["Next.js (واجهات تفاعلية)", "Node.js / Python (خلفية)", "Tailwind CSS (تصميم)", "Vercel / Upstash (استضافة وقواعد بيانات)"]
        },
        "target_audience_analysis": {
            "en": f"Ideal audience for {name} includes tech-savvy young professionals and middle-class consumers in major cities looking for convenience and premium services.",
            "ar": f"الجمهور المستهدف لـ {name} يشمل المهنيين الشباب المهتمين بالتكنولوجيا والمستهلكين من الطبقة المتوسطة في المدن الكبرى الذين يبحثون عن السهولة والخدمات الممتازة."
        }
    }

def get_local_swot(biz_type):
    if biz_type == "Restaurant":
        return {
            "en": {
                "strengths": ["High demand for online delivery", "Strong visual appeal for food products", "High customer lifetime value", "Easy local menu updates"],
                "weaknesses": ["Dependency on third-party delivery apps (high fees)", "Low margin per item", "Inconsistent customer data collection", "High staff turnover"],
                "opportunities": ["Create direct-to-consumer ordering system", "Implement automated loyalty rewards", "Hyper-local Google Map ads", "WhatsApp interactive menus"],
                "threats": ["Fierce local competition", "Rising ingredient and packaging costs", "Negative online reviews impacting reputation", "Economic price sensitivity"]
            },
            "ar": {
                "strengths": ["طلب مرتفع على التوصيل عبر الإنترنت", "جاذبية بصرية قوية للمأكولات", "قيمة عمرية عالية للعميل", "سهولة تحديث القائمة محلياً"],
                "weaknesses": ["الاعتماد على تطبيقات التوصيل الخارجية (رسوم مرتفعة)", "هوامش ربح منخفضة للوجبة", "عدم جمع بيانات العملاء بشكل منظم", "ارتفاع معدل دوران الموظفين"],
                "opportunities": ["إنشاء منصة طلب مباشرة لتجنب العمولات", "تطبيق برنامج ولاء ومكافآت تلقائي", "إعلانات جوجل المحلية المستهدفة للمنطقة", "منيو تفاعلي ذكي عبر واتساب"],
                "threats": ["المنافسة المحلية الشديدة", "ارتفاع تكاليف المكونات والتعبئة", "التقييمات السلبية عبر الإنترنت التي تؤثر على السمعة", "الحساسية الاقتصادية للأسعار"]
            }
        }
    elif biz_type == "Fashion":
        return {
            "en": {
                "strengths": ["Highly shareable and visual content", "Global shipping possibilities", "Strong potential for influencer partnerships", "Multiple design variations"],
                "weaknesses": ["High return rates due to sizing issues", "Intense price competition", "High cart abandonment rates", "High photography expenses"],
                "opportunities": ["Implement an AI size guide on the store", "Launch automated retargeting flows for cart recovery", "Leverage TikTok Shop / Instagram Checkout", "WhatsApp checkout catalogs"],
                "threats": ["Rapidly changing style trends", "Supply chain and inventory delays", "Platform algorithm changes impacting organic reach", "Low cost imports dominance"]
            },
            "ar": {
                "strengths": ["محتوى مرئي جذاب وسهل المشاركة", "إمكانيات شحن عالمية ومحلية واسعة", "إمكانيات قوية للشراكة مع المؤثرين", "تنوع كبير في خيارات التصميم"],
                "weaknesses": ["معدلات إرجاع عالية بسبب مقاسات الملابس", "منافسة سعرية شديدة جداً", "نسبة عالية لسلات التسوق المتروكة", "تكاليف تصوير عالية"],
                "opportunities": ["إضافة دليل مقاسات ذكي في المتجر", "إطلاق حملات إعادة استهداف تلقائية للسلات المتروكة", "استغلال البيع المباشر عبر تيك توك وإنستجرام", "منيو كتالوجات الدفع عبر واتساب"],
                "threats": ["تغير صيحات الموضة بسرعة كبيرة", "تأخيرات في سلسلة التوريد والمخزون", "تغييرات خوارزميات المنصات التي تؤثر على الوصول المجاني", "هيمنة المنتجات المستوردة منخفضة التكلفة"]
            }
        }
    elif biz_type == "Clinic":
        return {
            "en": {
                "strengths": ["High trust requirement builds strong patient relationships", "High search intent for medical specialties", "Word-of-mouth referral potential", "Stable recurring clinic visits"],
                "weaknesses": ["Time-bound services (limited capacity)", "Difficulty in showing patient results due to privacy", "High no-show rates for appointments", "High doctor dependencies"],
                "opportunities": ["Automated SMS/WhatsApp booking confirmation and reminders", "Telehealth integrations for remote consults", "SEO content detailing doctor authority", "Clinic app for medical history"],
                "threats": ["Competitor clinics offering lower consultation fees", "Negative Google reviews", "Strict regulations on medical advertising", "Talented staff attrition"]
            },
            "ar": {
                "strengths": ["طلب الثقة العالي يبني علاقات قوية مع المرضى", "معدل بحث مرتفع عن التخصصات الطبية", "إمكانية إحالة قوية عن طريق التوصيات الشخصية", "زيارات دورية مستقرة للعيادة"],
                "weaknesses": ["خدمات مرتبطة بالوقت (طاقة استيعابية محدودة)", "صعوبة عرض نتائج المرضى بسبب الخصوصية الطبية", "معدلات غياب عالية للمواعيد دون إلغاء مسبق", "اعتماد كامل على الطبيب"],
                "opportunities": ["تفعيل رسائل تأكيد ومواعيد تلقائية عبر واتساب/SMS", "تكامل الاستشارات عن بعد لزيادة الوصول", "تحسين محركات البحث للتركيز على خبرة الطبيب", "تطبيق عيادة لتتبع التاريخ الطبي للعميل"],
                "threats": ["عيادات منافسة تقدم أسعار كشف أقل", "التقييمات السلبية على خرائط جوجل", "لوائح وقوانين صارمة على الإعلانات الطبية", "تسرب الكفاءات الطبية والمساعدين"]
            }
        }
    else:
        return {
            "en": {
                "strengths": ["Unique positioning and agility", "Direct founder-customer communication", "Low initial operating overhead", "Niche marketing opportunities"],
                "weaknesses": ["Limited brand awareness", "Lack of specialized digital marketing expertise", "Tight budget constraints", "Lack of historical data"],
                "opportunities": ["Leverage niche SEO keywords to outrank big players", "Implement automated email marketing sequence", "Build a high-performance landing page targeting 1 primary action", "Strategic local partnerships"],
                "threats": ["Established competitors with large marketing budgets", "Rapid technological obsolescence", "High customer acquisition costs", "Economic changes"]
            },
            "ar": {
                "strengths": ["موقع فريد ومرونة عالية في اتخاذ القرار", "اتصال مباشر بين المؤسس والعميل", "تكاليف تشغيلية أولية منخفضة", "فرص تسويق متخصصة ومستهدفة"],
                "weaknesses": ["وعي محدود بالعلامة التجارية حالياً", "نقص الخبرة المتخصصة في التسويق الرقمي", "قيود ميزانية مشددة في البداية", "غياب البيانات التاريخية للنشاط"],
                "opportunities": ["استغلال الكلمات المفتاحية المتخصصة للتفوق على الكبار", "تطبيق سلسلة تسويق تلقائية عبر البريد/واتساب", "بناء صفحة هبوط عالية الأداء تركز على إجراء أساسي واحد", "شراكات استراتيجية محلية"],
                "threats": ["منافسون راسخون بميزانيات تسويقية ضخمة", "التقادم التكنولوجي السريع", "تكلفة عالية لاستحواذ العملاء الجدد", "التغيرات الاقتصادية المستمرة"]
            }
        }

def get_local_marketing_plan(biz_type):
    if biz_type == "Restaurant":
        return {
            "en": [
                "Visual Food Content: Post daily high-definition reels of food preparation on Instagram/TikTok.",
                "Local SEO Optimization: Set up Google Business Profile and actively collect reviews to rank in the Google Map Pack.",
                "Influencer Food Tastings: Invite local food bloggers in exchange for social media coverage.",
                "WhatsApp Broadcasts: Direct promotion on weekends to recurring customers with coupon codes."
            ],
            "ar": [
                "محتوى طعام مرئي: نشر مقاطع ريلز يومية عالية الدقة لتحضير الطعام على إنستجرام وتيك توك.",
                "تحسين محركات البحث المحلية: إعداد ملف جوجل التجاري وجمع التقييمات للظهور في نتائج خرائط جوجل الأولى.",
                "دعوة مدوني طعام: دعوة صناع المحتوى المهتمين بالطعام لتجربة قائمة الطعام مقابل تغطية على حساباتهم.",
                "رسائل واتساب الجماعية: إرسال عروض ترويجية مباشرة خلال عطلة نهاية الأسبوع للعملاء المميزين."
            ]
        }
    elif biz_type == "Fashion":
        return {
            "en": [
                "Micro-influencer Campaigns: Seed free products to creators with 5k-20k followers.",
                "Retargeting Ads: Run Meta catalog ads targeting users who added items to cart but did not purchase.",
                "User Generated Content: Run a contest encouraging customers to post photos wearing your brand.",
                "Flash Sales Events: Monthly exclusive 24-hour deals promoted via Instagram Stories countdown timers."
            ],
            "ar": [
                "حملات المؤثرين الصغار: إرسال منتجات مجانية لصناع محتوى الموضة الذين لديهم من 5 إلى 20 ألف متابع.",
                "إعلانات إعادة الاستهداف: تشغيل إعلانات كتالوج ميتا لاستهداف العملاء الذين أضافوا منتجات للسلة ولم يشتروا.",
                "المحتوى من صنع المستخدمين: إطلاق مسابقة تشجع العملاء على نشر صور بمنتجاتك مقابل فرصة لربح قسيمة شراء.",
                "أحداث المبيعات الخاطفة: عروض حصرية شهيرة مدتها 24 ساعة فقط باستخدام عدادات تنازلية في ستوري إنستجرام."
            ]
        }
    elif biz_type == "Clinic":
        return {
            "en": [
                "Educational Video Series: Short Q&A videos with the doctor explaining common myths on TikTok and Instagram.",
                "Google Search Ads: Target high-intent queries like 'best dermatologist near me' or 'cardiologist booking'.",
                "Patient Testimonial Videos: Video stories of patients sharing their successful journey.",
                "Local SEO Citations: Ensure consistent business listings on local directories like Vezeeta."
            ],
            "ar": [
                "سلسلة فيديوهات تعليمية: فيديوهات قصيرة للطبيب يجيب فيها عن أسئلة شائعة على تيك توك وإنستجرام.",
                "إعلانات بحث جوجل: استهداف الكلمات ذات النية العالية مثل 'أفضل طبيب جلدية بالقرب مني' أو 'حجز طبيب قلب'.",
                "فيديوهات تجارب المرضى: قصص مصورة لمرضى يشاركون رحلة علاجهم الناجحة (بعد أخذ موافقتهم).",
                "الظهور على المنصات المحلية: ضمان وجود الملف التجاري بنفس البيانات على منصات الحجز مثل فيزيتا والخرائط."
            ]
        }
    else:
        return {
            "en": [
                "Educational Blogging: Answer the top 20 questions your customers ask on Google.",
                "Direct Outreach: Use LinkedIn or cold WhatsApp outreach to target business clients (B2B).",
                "Case Study Funnel: Build a detailed case study page demonstrating how you solved a client's problem.",
                "Google Search Campaigns: Target active keyword searches matching your exact solutions."
            ],
            "ar": [
                "التدوين التعليمي: الإجابة على أكثر 20 سؤالاً يسألها عملاؤك على جوجل في مقالات متخصصة.",
                "التواصل المباشر: استخدام لينكد إن أو واتساب للتواصل المباشر مع العملاء من الشركات (B2B).",
                "قمع دراسة الحالة: بناء صفحة دراسة حالة مفصلة توضح كيف قمت بحل مشكلة عميل سابق بالتفصيل.",
                "حملات بحث جوجل: استهداف عمليات البحث الفعالة عن كلمات تدل على المشاكل التي تحلها خدماتك."
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
            "Keyword-Rich Headers: Structure pages using 1 principal H1 containing the main target keyword, followed by H2s and H3s.",
            "Alt Image Text: Always include keywords inside image description tags."
        ],
        "ar": [
            "تحسين مؤشرات أداء الويب الأساسية: التأكد من أن وقت تحميل صفحة الجوال أقل من 1.5 ثانية.",
            "بيانات Schema المنظمة: تطبيق كود سكيما (LocalBusiness أو Product) للحصول على نتائج غنية في جوجل.",
            "عناوين غنية بالكلمات المفتاحية: تنظيم الصفحات باستخدام عنوان رئيسي واحد H1 يحتوي الكلمة المستهدفة، يليه H2 ثم H3.",
            "وصف الصور Alt: كتابة كلمات مفتاحية في حقل الوصف البديل للصور لرفع ترتيبها في نتائج بحث الصور."
        ]
    }

def get_local_ai_summary(name, biz_type, challenge):
    return {
        "en": f"AI Strategy Overview for '{name}': As a {biz_type} business, your primary bottleneck is resolved by shifting focus from standard landing pages to an automated high-conversion system. By solving the '{challenge}' challenge, we estimate a direct increase in conversion rate by up to 45% using structured user experience designs.",
        "ar": f"نظرة عامة على استراتيجية الذكاء الاصطناعي لـ '{name}': كنشاط تجاري في مجال ({biz_type})، يتم حل العقبة الرئيسية لعملك عن طريق تحويل التركيز من صفحات الهبوط التقليدية إلى نظام أوتوماتيكي عالي التحويل. من خلال حل تحدي '{challenge}'، نقدر زيادة مباشرة في معدل التحويل تصل إلى 45% باستخدام تصاميم تجربة مستخدم منظمة."
    }
