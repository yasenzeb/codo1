// ===== translations =====
const I18N = {
  en: {
    dashboardTitle: "Business Analysis - Dashboard",
    backToHomeText: "Home",
    statusTitle: "Current Order Status",
    liveUpdates: "Live Updates",
    businessDetails: "Business Details",
    lblBizName: "Name",
    lblBizType: "Type",
    lblPhone: "Phone",
    lblEmail: "Email",
    lblSocials: "Social Media",
    businessScore: "Business Score",
    growthPotential: "Growth Potential",
    aiRecommendation: "AI Recommendation Strategy",
    keyFeatures: "Recommended Technical Features:",
    swotTitle: "Project SWOT Analysis",
    swotStrengths: "Strengths",
    swotWeaknesses: "Weaknesses",
    swotOpportunities: "Opportunities",
    swotThreats: "Threats",
    actionPlan: "Roadmap (30 Days)",
    marketingPlan: "Marketing & Growth Tactics",
    seoTips: "SEO & Performance Checklist",
    status_pending: "Pending",
    desc_pending: "Your order is currently under review by our team. Updates will appear here in real-time.",
    status_approved: "Approved",
    desc_approved: "Congratulations! Your order has been approved. Our team is now working on your implementation.",
    status_rejected: "Rejected",
    desc_rejected: "This order has been rejected. Please check your phone or email for details or reach out to support.",
    status_suspended: "On Hold",
    desc_suspended: "This order is currently suspended/on hold. We might need extra details to proceed.",
    // New specs translations
    lblProjectDesc: "Project Description",
    lblBudgetRange: "Budget",
    lblPreferredColors: "Preferred Colors",
    lblTargetAudience: "Target Audience",
    lblCompetitors: "Competitors",
    lblHasWebsite: "Current Website",
    costDevDetails: "Implementation & Cost details",
    lblDeveloper: "Assigned Developer",
    lblCost: "Total Cost",
    lblPaymentStatus: "Payment Status",
    errOrderNotFound: "Order Not Found",
    errOrderNotFoundDesc: "Sorry, this order is not available in the system or has been deleted by administration.",
    optNoWebsite: "None",
    pay_unpaid: "❌ Unpaid / العربون مستحق",
    pay_paid: "✅ Paid"
  },
  ar: {
    dashboardTitle: "تحليل النشاط التجاري - لوحة التحكم",
    backToHomeText: "الرئيسية",
    statusTitle: "حالة الطلب الحالية",
    liveUpdates: "تحديث مباشر",
    businessDetails: "تفاصيل النشاط",
    lblBizName: "اسم النشاط",
    lblBizType: "نوع النشاط",
    lblPhone: "رقم الهاتف",
    lblEmail: "البريد الإلكتروني",
    lblSocials: "وسائل التواصل",
    businessScore: "تقييم النشاط التجاري",
    growthPotential: "إمكانية النمو",
    aiRecommendation: "توصية الذكاء الاصطناعي",
    keyFeatures: "الميزات التقنية المقترحة:",
    swotTitle: "تحليل SWOT للمشروع",
    swotStrengths: "نقاط القوة (Strengths)",
    swotWeaknesses: "نقاط الضعف (Weaknesses)",
    swotOpportunities: "الفرص المتاحة (Opportunities)",
    swotThreats: "التهديدات والمخاطر (Threats)",
    actionPlan: "خارطة الطريق التنفيذية (30 يوماً)",
    marketingPlan: "أفكار تسويق وجذب العملاء",
    seoTips: "توصيات تحسين محركات البحث والسرعة (SEO)",
    status_pending: "قيد الانتظار",
    desc_pending: "طلبك قيد المراجعة حالياً من قبل فريق العمل. يمكنك متابعة التحديثات هنا فوراً.",
    status_approved: "تم تأكيد الطلب",
    desc_approved: "تهانينا! تم تأكيد طلبك والبدء في التنفيذ. فريقنا بدأ العمل على مشروعك وسنتصل بك قريباً.",
    status_rejected: "تم رفض الطلب",
    desc_rejected: "تم رفض هذا الطلب. يرجى مراجعة بريدك الإلكتروني أو الاتصال بالدعم لمعرفة الأسباب.",
    status_suspended: "معلق مؤقتاً",
    desc_suspended: "تم تعليق طلبك مؤقتاً. ربما نحتاج إلى معلومات إضافية لتفعيل الطلب.",
    // New specs translations
    lblProjectDesc: "وصف المشروع",
    lblBudgetRange: "الميزانية",
    lblPreferredColors: "الألوان المفضلة",
    lblTargetAudience: "الجمهور المستهدف",
    lblCompetitors: "المنافسين",
    lblHasWebsite: "الموقع الحالي",
    costDevDetails: "تفاصيل التنفيذ والتكلفة",
    lblDeveloper: "المطور المسؤول",
    lblCost: "التكلفة الإجمالية",
    lblPaymentStatus: "حالة الدفع",
    errOrderNotFound: "الطلب غير متوفر",
    errOrderNotFoundDesc: "عذراً، هذا الطلب غير موجود في النظام أو تم حذفه نهائياً من قبل الإدارة.",
    optNoWebsite: "لا يوجد",
    pay_unpaid: "❌ لم يتم دفع العربون",
    pay_paid: "✅ تم تأكيد الدفع والبدء بالعمل"
  }
};

// State
let currentLang = "ar";
let orderId = null;
let orderData = null;

// Parse URL Param
function getOrderIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

// Switch Language
function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  
  // Update translation keys
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const k = el.getAttribute("data-i18n");
    if (I18N[lang][k] !== undefined) el.textContent = I18N[lang][k];
  });
  
  document.getElementById("btnEn").classList.toggle("active", lang === "en");
  document.getElementById("btnAr").classList.toggle("active", lang === "ar");
  
  // Re-render components with translated content
  if (orderData) {
    renderOrderInfo();
    renderAnalysisData();
  }
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

// Theme Toggle (Light / Dark)
function initTheme() {
  const themeToggle = document.getElementById("themeToggle");
  const storedTheme = localStorage.getItem("theme") || "dark"; // Default to dark for premium look
  
  if (storedTheme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  
  themeToggle.addEventListener("click", () => {
    const isDark = document.documentElement.classList.contains("dark");
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    }
  });
}

// Collapsible Simulator Card
function initSimulatorCollapse() {
  const header = document.getElementById("simulatorHeader");
  const card = document.querySelector(".simulator-card");
  header.addEventListener("click", () => {
    card.classList.toggle("collapsed");
  });
}

// Fetch Order Data from server
async function fetchOrder() {
  if (!orderId) return;
  try {
    const res = await fetch(`/api/order/${orderId}`);
    if (res.status === 200) {
      const data = await res.json();
      if (data.ok) {
        orderData = data.order;
        updateStatusWidget(orderData.status);
        
        // Hide error and show container in case it was toggled
        document.querySelector(".dash-container").style.display = "grid";
        document.getElementById("errorView").style.display = "none";

        // Only render the static data once on load, to prevent layout flashing
        if (!document.getElementById("infoName").textContent || document.getElementById("infoName").textContent === "-") {
          renderOrderInfo();
          renderAnalysisData();
        } else {
          // Keep updating Cost, Dev, and Payment Status dynamically
          document.getElementById("infoDeveloper").textContent = orderData.developer || "-";
          document.getElementById("infoCost").textContent = orderData.cost || "-";
          
          const payEl = document.getElementById("infoPaymentStatus");
          if (orderData.payment_status === "paid") {
            payEl.textContent = I18N[currentLang].pay_paid;
            payEl.style.color = "hsl(var(--status-approved-fg))";
          } else {
            payEl.textContent = I18N[currentLang].pay_unpaid;
            payEl.style.color = "hsl(var(--status-rejected-fg))";
          }
        }
      }
    } else {
      // Order not found or deleted
      document.querySelector(".dash-container").style.display = "none";
      document.getElementById("errorView").style.display = "flex";
      if (typeof lucide !== "undefined") {
        lucide.createIcons();
      }
    }
  } catch (err) {
    console.error("Error fetching order status:", err);
  }
}

// Update the Status Widget dynamically
function updateStatusWidget(status) {
  const badge = document.getElementById("statusBadge");
  const statusTxt = document.getElementById("statusText");
  const statusDesc = document.getElementById("statusDesc");
  const statusIcon = document.getElementById("statusIcon");
  
  badge.className = `status-badge ${status}`;
  
  // Set Vector Icon
  let iconName = "clock";
  if (status === "approved") iconName = "check-circle-2";
  else if (status === "rejected") iconName = "x-circle";
  else if (status === "suspended") iconName = "pause-circle";
  
  if (statusIcon) {
    statusIcon.innerHTML = `<i data-lucide="${iconName}" style="width: 18px; height: 18px;"></i>`;
  }
  
  // Set Text & Description from language bundle
  statusTxt.textContent = I18N[currentLang][`status_${status}`] || status;
  statusDesc.textContent = I18N[currentLang][`desc_${status}`] || "";
  
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

// Render business info
function renderOrderInfo() {
  if (!orderData) return;
  
  document.getElementById("infoName").textContent = orderData.business_name;
  
  // Type translation if available in options mapping
  document.getElementById("infoType").textContent = orderData.business_type;
  document.getElementById("infoPhone").textContent = orderData.phone;
  document.getElementById("infoEmail").textContent = orderData.email || "N/A";
  
  // Social links formatting
  const socials = orderData.socials || {};
  const socContainer = document.getElementById("infoSocials");
  if (socContainer) {
    socContainer.innerHTML = "";
    if (socials.instagram) {
      const link = socials.instagram.startsWith("http") ? socials.instagram : `https://instagram.com/${socials.instagram}`;
      socContainer.innerHTML += `<a href="${link}" target="_blank" class="social-badge" style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle;"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>Instagram</a>`;
    }
    if (socials.tiktok) {
      const link = socials.tiktok.startsWith("http") ? socials.tiktok : `https://tiktok.com/@${socials.tiktok}`;
      socContainer.innerHTML += `<a href="${link}" target="_blank" class="social-badge" style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle;"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/></svg>TikTok</a>`;
    }
    if (socials.facebook) {
      const link = socials.facebook.startsWith("http") ? socials.facebook : `https://facebook.com/${socials.facebook}`;
      socContainer.innerHTML += `<a href="${link}" target="_blank" class="social-badge" style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle;"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>Facebook</a>`;
    }
    
    if (socContainer.innerHTML === "") {
      socContainer.innerHTML = `<span style="color: var(--muted-foreground)">-</span>`;
    }
  }

  // Populate new details
  document.getElementById("infoProjectDesc").textContent = orderData.project_description || "-";
  document.getElementById("infoBudget").textContent = orderData.budget_range || "-";
  document.getElementById("infoColors").textContent = orderData.preferred_colors || "-";
  document.getElementById("infoAudience").textContent = orderData.target_audience || "-";
  document.getElementById("infoCompetitors").textContent = orderData.competitors || "-";
  
  const webEl = document.getElementById("infoWebsite");
  if (orderData.has_existing_website && orderData.existing_website_url) {
    webEl.innerHTML = `<a href="${orderData.existing_website_url}" target="_blank" style="color: hsl(var(--primary)); text-decoration: underline; word-break: break-all;">${orderData.existing_website_url}</a>`;
  } else {
    webEl.textContent = I18N[currentLang].optNoWebsite;
  }

  // Cost, dev, payment
  document.getElementById("infoDeveloper").textContent = orderData.developer || "-";
  document.getElementById("infoCost").textContent = orderData.cost || "-";
  
  const payEl = document.getElementById("infoPaymentStatus");
  if (orderData.payment_status === "paid") {
    payEl.textContent = I18N[currentLang].pay_paid;
    payEl.style.color = "hsl(var(--status-approved-fg))";
  } else {
    payEl.textContent = I18N[currentLang].pay_unpaid;
    payEl.style.color = "hsl(var(--status-rejected-fg))";
  }
}

// Render AI Analysis charts and strategies
function renderAnalysisData() {
  if (!orderData || !orderData.analysis) return;
  
  const analysis = orderData.analysis;
  
  // Brand title
  document.getElementById("brandTitle").textContent = `${orderData.business_name} - AI Dashboard`;
  
  // Metrics progress bar animation
  document.getElementById("valScore").textContent = `${analysis.score}/100`;
  document.getElementById("scoreBar").style.width = `${analysis.score}%`;
  
  document.getElementById("valGrowth").textContent = `${analysis.growth_potential}%`;
  document.getElementById("growthBar").style.width = `${analysis.growth_potential}%`;
  
  // Solution Header & Summary
  const solText = orderData.business_type === "Restaurant" || orderData.business_type === "مطعم"
    ? (currentLang === "ar" ? "منصة طلبات أونلاين ذكية ونظام توصيل مباشر" : "Direct-to-consumer smart ordering platform")
    : (currentLang === "ar" ? "منصة نمو رقمي وتجربة عملاء مخصصة" : "Automated digital growth platform");
  
  document.getElementById("solutionTitle").textContent = solText;
  document.getElementById("aiSummary").textContent = analysis.ai_summary[currentLang];
  
  // Key Features
  const features = analysis.swot[currentLang].opportunities.slice(0, 4); // fallbacks
  const featsList = document.getElementById("featuresList");
  featsList.innerHTML = "";
  
  // Let's get specific features based on type
  let typeFeats = ["High speed performance", "SEO optimization", "Mobile responsive design", "Analytics integration"];
  if (orderData.business_type === "Restaurant" || orderData.business_type === "مطعم") {
    typeFeats = currentLang === "ar" 
      ? ["منصة طلبات سريعة للجوال", "تكامل مع خرائط جوجل", "برنامج ولاء ونقاط تلقائي", "إدارة وتعديل القائمة الرقمية"]
      : ["Mobile Fast Ordering", "Google Map Optimization", "Loyalty Point Engine", "Digital Menu Manager"];
  } else if (orderData.business_type === "Fashion" || orderData.business_type === "أزياء") {
    typeFeats = currentLang === "ar"
      ? ["معرض منتجات ذكي", "أتمتة سلات الشراء المتروكة", "كوبونات خصم تفاعلية", "تكامل مع انستغرام وشوب"]
      : ["Smart Product Showcase", "Abandoned Cart Automation", "Interactive Coupons", "Instagram Feed Sync"];
  } else if (orderData.business_type === "Clinic" || orderData.business_type === "عيادة") {
    typeFeats = currentLang === "ar"
      ? ["نظام حجز مواعيد فوري", "تذكير بالواتساب وتأكيد تلقائي", "ملف تعريفي كامل للأطباء", "قسم مراجعات وتقييمات للمرضى"]
      : ["Instant Booking Portal", "WhatsApp Auto-Reminders", "Doctor Profiles", "Patient Review Section"];
  } else {
    typeFeats = currentLang === "ar"
      ? ["صفحة هبوط عالية التحويل", "نظام أتمتة جمع البيانات", "تكامل مع نظام CRM", "تحليلات متقدمة لمصادر الزوار"]
      : ["High-Conversion Landing", "Lead Automation Flow", "CRM Integrations", "Traffic Source Analytics"];
  }
  
  typeFeats.forEach(f => {
    featsList.innerHTML += `<li>${f}</li>`;
  });
  
  // SWOT List
  const swot = analysis.swot[currentLang];
  populateList("swotStrengthsList", swot.strengths);
  populateList("swotWeaknessesList", swot.weaknesses);
  populateList("swotOpportunitiesList", swot.opportunities);
  populateList("swotThreatsList", swot.threats);
  
  // Action Roadmap
  const roadmap = analysis.action_plan[currentLang];
  const roadmapContainer = document.getElementById("actionPlanList");
  roadmapContainer.innerHTML = "";
  
  roadmap.forEach((step, idx) => {
    const title = step.split(" - ")[0] || `Step ${idx+1}`;
    const desc = step.split(" - ")[1] || step;
    
    roadmapContainer.innerHTML += `
      <div class="roadmap-item">
        <div class="roadmap-dot"></div>
        <div class="roadmap-title">${title}</div>
        <div class="roadmap-desc">${desc}</div>
      </div>
    `;
  });
  
  // Marketing & SEO
  populateList("marketingPlanList", analysis.marketing_plan[currentLang]);
  populateList("seoTipsList", analysis.seo_tips[currentLang]);
  
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

function populateList(elementId, itemsArray) {
  const ul = document.getElementById(elementId);
  ul.innerHTML = "";
  itemsArray.forEach(item => {
    ul.innerHTML += `<li>${item}</li>`;
  });
}

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
  orderId = getOrderIdFromUrl();
  if (!orderId) {
    alert("رقم طلب غير صحيح أو منتهي!");
    window.location.href = "/";
    return;
  }
  
  initTheme();
  setLanguage("ar"); // Default to Arabic
  
  // Fetch initial details
  fetchOrder();
  
  // Poll order status every 2 seconds (dynamic updates)
  setInterval(fetchOrder, 2000);
  
  // Language button event listeners
  document.getElementById("btnEn").addEventListener("click", () => setLanguage("en"));
  document.getElementById("btnAr").addEventListener("click", () => setLanguage("ar"));
  
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
});
