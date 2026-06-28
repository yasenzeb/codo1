// ===== translations =====
const I18N = {
  en: {
    eyebrow: "Digital Product Agency",
    headline: "We help businesses grow through premium digital experiences.",
    sub: "Not just websites. Products that increase trust, conversions, and revenue.",
    cta: "Analyze my business",
    footnote: "No commitment required",
    question: "Question", of: "of", complete: "complete",
    back: "Back", continue: "Continue", analyze: "Analyze",
    analyzing: "Analyzing", business: "Business",
    buildingStrategy: "Building your strategy",
    analysisComplete: "Analysis Complete", your: "Your",
    resultSub: "Based on your answers, here is our recommended strategy.",
    businessScore: "Business Score", growthPotential: "Growth Potential",
    timeline: "Timeline", investment: "Investment", roi: "ROI Estimate",
    recommendedSolution: "Recommended Solution", keyFeatures: "Key Features:",
    seeCases: "See how we helped similar businesses",
    // Form translations
    formTitle: "Enter your business details",
    formDesc: "Please fill out this form to complete your AI-powered business analysis.",
    lblBizName: "Business Name",
    lblBizType: "Business Type",
    lblBizPhone: "Phone Number",
    errPhone: "Please enter a valid Egyptian phone number (e.g. 01xxxxxxxxx)",
    lblBizEmail: "Email Address (Optional)",
    lblSocials: "Social Media Links (Optional)",
    submitForm: "Submit & Analyze",
    trackOrder: "Track My Current Order"
  },
  ar: {
    eyebrow: "وكالة منتجات رقمية",
    headline: "نساعد الشركات على النمو من خلال تجارب رقمية متميزة.",
    sub: "ليست مجرد مواقع. منتجات تزيد الثقة والتحويلات والإيرادات.",
    cta: "حلّل نشاطي التجاري",
    footnote: "لا يتطلب أي التزام",
    question: "سؤال", of: "من", complete: "مكتمل",
    back: "رجوع", continue: "متابعة", analyze: "حلّل",
    analyzing: "جارٍ تحليل", business: "",
    buildingStrategy: "نبني استراتيجيتك",
    analysisComplete: "اكتمل التحليل", your: "نشاطك",
    resultSub: "بناءً على إجاباتك، هذه استراتيجيتنا الموصى بها.",
    businessScore: "تقييم النشاط", growthPotential: "إمكانية النمو",
    timeline: "الجدول الزمني", investment: "الاستثمار", roi: "العائد المتوقع",
    recommendedSolution: "الحل الموصى به", keyFeatures: "الميزات الرئيسية:",
    seeCases: "شاهد كيف ساعدنا شركات مشابهة",
    // Form translations
    formTitle: "أدخل بيانات نشاطك التجاري",
    formDesc: "الرجاء إدخال البيانات التالية لإكمال تحليل الذكاء الاصطناعي الخاص بك.",
    lblBizName: "اسم النشاط التجاري",
    lblBizType: "نوع النشاط التجاري",
    lblBizPhone: "رقم الهاتف",
    errPhone: "الرجاء إدخال رقم هاتف مصري صحيح (مثال: 01xxxxxxxxx)",
    lblBizEmail: "البريد الإلكتروني (اختياري)",
    lblSocials: "حسابات التواصل الاجتماعي (اختياري)",
    submitForm: "إرسال وتحليل",
    trackOrder: "متابعة طلبي الحالي"
  }
};

// ===== questions =====
const QUESTIONS = {
  en: [
    { title: "What type of business are you?", desc: "This helps us show you the most relevant case studies.",
      options: ["Restaurant","Fashion","Clinic","Corporate","Startup","Other"] },
    { title: "Where do your customers come from?", desc: "Select all that apply.",
      options: ["Instagram","Facebook","TikTok","WhatsApp","Google","Offline"], multi: true },
    { title: "What is your biggest challenge?", desc: "Be honest — we will tailor the solution to your needs.",
      options: ["Sales & Revenue","Brand Image","Customer Trust","Manual Processes","Outdated Website","Other"] },
    { title: "When do you want to launch?", desc: "This affects our recommended approach.",
      options: ["ASAP","Within 2 weeks","Within a month","Flexible timeline"] },
    { title: "Where are you in the process?", desc: "This helps us prepare for our conversation.",
      options: ["Just researching","Ready to start soon","Need a proposal today"] },
  ],
  ar: [
    { title: "ما نوع نشاطك التجاري؟", desc: "يساعدنا هذا في عرض دراسات الحالة الأكثر صلة.",
      options: ["مطعم","أزياء","عيادة","شركة","ناشئة","آخر"] },
    { title: "من أين يأتي عملاؤك؟", desc: "اختر كل ما ينطبق.",
      options: ["انستغرام","فيسبوك","تيك توك","واتساب","جوجل","أوفلاين"], multi: true },
    { title: "ما أكبر تحدٍ تواجهه؟", desc: "كن صريحًا — سنخصص الحل وفق احتياجاتك.",
      options: ["المبيعات والإيرادات","صورة العلامة","ثقة العملاء","العمليات اليدوية","موقع قديم","آخر"] },
    { title: "متى تريد الإطلاق؟", desc: "هذا يؤثر على المنهجية الموصى بها.",
      options: ["في أقرب وقت","خلال أسبوعين","خلال شهر","جدول مرن"] },
    { title: "في أي مرحلة أنت الآن؟", desc: "يساعدنا هذا في تجهيز محادثتنا.",
      options: ["مجرد بحث","مستعد للبدء قريبًا","أحتاج عرض اليوم"] },
  ]
};

const LOAD_STEPS = {
  en: ["Analyzing competitors...","Reviewing market...","Calculating opportunities...","Generating recommendations...","Preparing roadmap..."],
  ar: ["تحليل المنافسين...","مراجعة السوق...","حساب الفرص...","إنشاء التوصيات...","إعداد خارطة الطريق..."]
};

// ===== state =====
const state = {
  lang: "en",
  step: 0,
  answers: {},
  total: 5,
};

// ===== lang =====
function setLang(lang){
  state.lang = lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach(el=>{
    const k = el.getAttribute("data-i18n");
    if (I18N[lang][k] !== undefined) el.textContent = I18N[lang][k];
  });
  
  // Custom placeholders/labels since they can't be set by textContent easily
  const nameInp = document.getElementById("bizName");
  const phoneInp = document.getElementById("bizPhone");
  const emailInp = document.getElementById("bizEmail");
  const instaInp = document.getElementById("bizInstagram");
  const tiktokInp = document.getElementById("bizTiktok");
  const fbInp = document.getElementById("bizFacebook");
  
  if (lang === "ar") {
    if (nameInp) nameInp.placeholder = "مثال: مطعمي المتميز";
    if (phoneInp) phoneInp.placeholder = "مثال: 01012345678";
    if (emailInp) emailInp.placeholder = "مثال: name@domain.com";
    if (instaInp) instaInp.placeholder = "اسم المستخدم أو الرابط";
    if (tiktokInp) tiktokInp.placeholder = "اسم المستخدم أو الرابط";
    if (fbInp) fbInp.placeholder = "اسم المستخدم أو رابط الصفحة";
  } else {
    if (nameInp) nameInp.placeholder = "e.g. My Awesome Brand";
    if (phoneInp) phoneInp.placeholder = "e.g. 01012345678";
    if (emailInp) emailInp.placeholder = "e.g. name@domain.com";
    if (instaInp) instaInp.placeholder = "Instagram Username / URL";
    if (tiktokInp) tiktokInp.placeholder = "TikTok Username / URL";
    if (fbInp) fbInp.placeholder = "Facebook Profile / URL";
  }

  document.querySelectorAll(".lang-btn").forEach(b=>b.classList.toggle("active", b.dataset.lang===lang));
  
  // if quiz visible, redraw
  if (document.getElementById("view-quiz").classList.contains("active")) renderQuestion();
}
document.querySelectorAll(".lang-btn").forEach(b=>b.addEventListener("click",()=>setLang(b.dataset.lang)));

// ===== views =====
function show(id){
  document.querySelectorAll(".view").forEach(v=>v.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

// ===== quiz =====
const optionsEl = document.getElementById("options");
const qTitle = document.getElementById("qTitle");
const qDesc = document.getElementById("qDesc");
const qNow = document.getElementById("qNow");
const qPct = document.getElementById("qPct");
const progressBar = document.getElementById("progressBar");
const continueBtn = document.getElementById("continueBtn");
const backBtn = document.getElementById("backBtn");

function renderQuestion(){
  const q = QUESTIONS[state.lang][state.step];
  qTitle.textContent = q.title;
  qDesc.textContent = q.desc;
  qNow.textContent = state.step + 1;
  const pct = Math.round(((state.step+1)/state.total)*100);
  qPct.textContent = pct;
  progressBar.style.width = pct + "%";
  optionsEl.innerHTML = "";

  // BUG FIX: check for undefined and null explicitly, because 0 is falsy
  const selected = (state.answers[state.step] !== undefined && state.answers[state.step] !== null) 
    ? state.answers[state.step] 
    : (q.multi ? [] : null);

  q.options.forEach((opt,i)=>{
    const btn = document.createElement("button");
    btn.className = "option";
    btn.textContent = opt;
    btn.type = "button";
    
    const isSel = q.multi ? selected.includes(i) : selected === i;
    if (isSel) btn.classList.add("selected");
    
    btn.addEventListener("click",()=>{
      if (q.multi){
        // Ensure we get a fresh array or mutate properly
        const arr = Array.isArray(state.answers[state.step]) ? [...state.answers[state.step]] : [];
        const idx = arr.indexOf(i);
        if (idx > -1) arr.splice(idx,1); else arr.push(i);
        state.answers[state.step] = arr;
      } else {
        state.answers[state.step] = i;
      }
      renderQuestion();
    });
    optionsEl.appendChild(btn);
  });
  
  const has = q.multi 
    ? (selected && selected.length > 0) 
    : (selected !== null && selected !== undefined);
    
  continueBtn.disabled = !has;
  continueBtn.textContent = state.step === state.total-1 ? I18N[state.lang].continue : I18N[state.lang].continue;
  backBtn.disabled = state.step === 0;
}

document.getElementById("startQuiz").addEventListener("click",()=>{
  state.step = 0; 
  state.answers = {};
  show("view-quiz"); 
  renderQuestion();
});

backBtn.addEventListener("click",()=>{ 
  if(state.step > 0){
    state.step--;
    renderQuestion();
  }
});

continueBtn.addEventListener("click",()=>{
  if (state.step < state.total - 1){ 
    state.step++; 
    renderQuestion(); 
  } else {
    showFormView();
  }
});

// ===== Form Section =====
const formView = document.getElementById("view-form");
const businessForm = document.getElementById("businessForm");
const formBackBtn = document.getElementById("formBackBtn");
const bizPhoneInp = document.getElementById("bizPhone");
const phoneError = document.getElementById("phoneError");

function showFormView() {
  show("view-form");
  // Pre-fill business type from Question 1 selection
  const selectedTypeIndex = state.answers[0];
  const typeText = QUESTIONS[state.lang][0].options[selectedTypeIndex];
  document.getElementById("bizType").value = typeText;
  
  // Hide previous errors
  phoneError.style.display = "none";
}

formBackBtn.addEventListener("click", () => {
  state.step = state.total - 1;
  show("view-quiz");
  renderQuestion();
});

// Validate phone format on input change
bizPhoneInp.addEventListener("input", () => {
  const cleaned = bizPhoneInp.value.replace(/\s+/g, "");
  const isEgypt = /^(\+?2?01[0125]\d{8})$|^(\+?2?1[0125]\d{8})$/.test(cleaned);
  if (isEgypt || cleaned === "") {
    phoneError.style.display = "none";
  } else {
    phoneError.style.display = "block";
  }
});

businessForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const phoneVal = bizPhoneInp.value.replace(/\s+/g, "");
  const isEgypt = /^(\+?2?01[0125]\d{8})$|^(\+?2?1[0125]\d{8})$/.test(phoneVal);
  
  if (!isEgypt) {
    phoneError.style.display = "block";
    bizPhoneInp.focus();
    return;
  }
  
  phoneError.style.display = "none";
  
  // Disable submit button
  const submitBtn = document.getElementById("formSubmitBtn");
  submitBtn.disabled = true;
  
  // Build payload
  const bizTypeIndex = state.answers[0];
  const bizTypeEn = QUESTIONS.en[0].options[bizTypeIndex];
  
  const payload = {
    lang: state.lang,
    business_name: document.getElementById("bizName").value.trim(),
    business_type: bizTypeEn,
    phone: phoneVal,
    email: document.getElementById("bizEmail").value.trim(),
    socials: {
      instagram: document.getElementById("bizInstagram").value.trim(),
      tiktok: document.getElementById("bizTiktok").value.trim(),
      facebook: document.getElementById("bizFacebook").value.trim()
    },
    answers: QUESTIONS.en.map((q, idx) => {
      const a = state.answers[idx];
      let val;
      if (q.multi) {
        val = Array.isArray(a) ? a.map(i => q.options[i]) : [];
      } else {
        val = (a !== undefined && a !== null) ? q.options[a] : "";
      }
      return { question: q.title, answer: val };
    })
  };
  
  // Show loading
  runLoadingSteps(payload);
});

// ===== loading and submit =====
function runLoadingSteps(payload){
  document.getElementById("loadBiz").textContent = QUESTIONS[state.lang][0].options[state.answers[0]];
  const stepsEl = document.getElementById("loadSteps");
  const steps = LOAD_STEPS[state.lang];
  stepsEl.innerHTML = "";
  steps.forEach(s=>{
    const li = document.createElement("li");
    li.textContent = s;
    stepsEl.appendChild(li);
  });
  
  show("view-loading");
  
  let i = 0;
  const items = stepsEl.querySelectorAll("li");
  items[0].classList.add("active");
  
  // Submit request asynchronously
  const submitPromise = fetch("/api/submit-order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(res => res.json()).catch(err => ({ ok: false, error: err.message }));
  
  const interval = setInterval(()=>{
    items[i].classList.remove("active");
    items[i].classList.add("done");
    i++;
    if (i >= items.length){
      clearInterval(interval);
      // Wait for submission to complete before redirecting
      submitPromise.then(data => {
        document.getElementById("formSubmitBtn").disabled = false;
        if (data.ok) {
          localStorage.setItem("current_order_id", data.order_id);
          setTimeout(() => {
            window.location.href = `/dashboard.html?id=${data.order_id}`;
          }, 300);
        } else {
          alert(data.error || "Submission failed. Please check backend connection.");
          show("view-form");
        }
      });
    } else {
      items[i].classList.add("active");
    }
  }, 700);
}

// Check for existing order to show Track Order button
function checkExistingOrder() {
  const currentOrderId = localStorage.getItem("current_order_id");
  const trackBtn = document.getElementById("trackOrderBtn");
  if (currentOrderId && trackBtn) {
    trackBtn.style.display = "inline-flex";
    trackBtn.addEventListener("click", () => {
      window.location.href = `/dashboard.html?id=${currentOrderId}`;
    });
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  setLang("ar"); // Default to Arabic as requested by user
  checkExistingOrder();
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
});
