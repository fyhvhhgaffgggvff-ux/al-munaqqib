import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import lasio
import google.generativeai as genai

# ---------------------------------------------------------
# إعدادات الصفحة والتنسيق العام
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة المُنقّب الهندسية",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحسين المظهر وإلغاء التداخلات على شاشات الجوال
st.markdown("""
    <style>
    /* تحسين الخطوط والتنسيق العام */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* تنسيق بطاقات النتائج */
    .stMetricCard {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    /* إخفاء القوائم غير الضرورية لتكبير مساحة العرض */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ضبط التبويبات لتظهر بوضوح بدون تداخل */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #0f172a;
        border-radius: 8px;
        color: #e2e8f0;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# العنوان الرئيسي
# ---------------------------------------------------------
st.title("⚡ منصة المُنقّب الهندسية")
st.caption("نظام شامل لتصميم أجهزة الرفع الصناعي، تحليل المكامن، واستشارات AI")

# ---------------------------------------------------------
# القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    api_key = st.text_input("مفتاح Gemini API:", type="password", help="أدخل مفتاح API لتفعيل الاستشارات الذكية")
    st.divider()
    st.info("💡 **المُنقّب v3.0**: أداة هندسية متكاملة لمهندسي النفط والإنتاج.")

# ---------------------------------------------------------
# الواجهة الرئيسية المنسقة عبر التبويبات
# ---------------------------------------------------------
tabs = st.tabs([
    "🎯 الترشيح الذكي", 
    "⚙️ تصميم SRP", 
    "⚡ تصميم ESP", 
    "📈 منحنى IPR", 
    "📁 تحليل الملفات", 
    "🤖 المساعد الذكي"
])

# 1. الترشيح الذكي
with tabs[0]:
    st.subheader("🎯 نظام الاختيار والترشيح الآلي")
    c1, c2 = st.columns(2)
    with c1:
        q_target = st.number_input("الانتاج المستهدف (BPD):", value=2000, step=100)
        depth_ft = st.number_input("العمق العمودي (ft):", value=6500, step=500)
    with c2:
        gor = st.number_input("نسبة الغاز للنفط GOR:", value=400, step=50)
        visc = st.number_input("اللزوجة (cP):", value=10.0, step=1.0)
        
    if st.button("ترشيح النظام المناسب 🔍", use_container_width=True):
        if q_target > 3000 and gor < 1000:
            st.success("RECOMMENDED: **المضخة الغاطسة (ESP)** - مناسبة لمعدلات الإنتاج العالية.")
        elif gor > 800:
            st.success("RECOMMENDED: **الرفع بالغاز (Gas Lift)** - ممتاز للآبار ذات نسبة الغاز العالية.")
        else:
            st.success("RECOMMENDED: **مضخة المكبس (SRP)** - الخيار الكلاسيكي الأمثل لهذه المعطيات.")

# 2. تصميم SRP
with tabs[1]:
    st.subheader("⚙️ تصميم مضخات المكبس (Sucker Rod Pump)")
    col1, col2 = st.columns(2)
    with col1:
        d_srp = st.number_input("عمق المضخة (ft):", value=5000, key="dsrp")
        q_srp = st.number_input("الإنتاج (BPD):", value=300, key="qsrp")
    with col2:
        s_len = st.number_input("طول الشوط (in):", value=86, key="slen")
        spm = st.number_input("عدد الأشواط (SPM):", value=12, key="spm")
        
    p_size = np.sqrt(q_srp / (0.1166 * s_len * spm * 0.8)) if (s_len * spm) > 0 else 1.5
    peak_l = (0.433 * d_srp * (np.pi * (p_size/2)**2)) + (d_srp * 1.6)
    hp_req = (peak_l * s_len * spm) / 375000 + 5
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("قطر المكبس", f"{p_size:.2f} in")
    m2.metric("أقصى حمل (Peak Load)", f"{peak_l:,.0f} lbs")
    m3.metric("قدرة المحرك", f"{hp_req:.1f} HP")

# 3. تصميم ESP
with tabs[2]:
    st.subheader("⚡ تصميم المضخات الكهربائية الغاطسة (ESP)")
    col1, col2 = st.columns(2)
    with col1:
        d_esp = st.number_input("عمق التركيب (ft):", value=7500, key="desp")
        q_esp = st.number_input("معدل التدفق (BPD):", value=4000, key="qesp")
    with col2:
        h_stg = st.number_input("الرفع لكل مرحلة (ft):", value=25, key="hstg")
        p_surf = st.number_input("الضغط السطحي (psi):", value=200, key="psurf")
        
    tdh = d_esp + (p_surf * 2.31)
    stages = int(tdh / h_stg) if h_stg > 0 else 100
    esp_hp = (q_esp * tdh) / 135000
    
    st.divider()
    e1, e2, e3 = st.columns(3)
    e1.metric("إجمالي الرفع (TDH)", f"{tdh:,.0f} ft")
    e2.metric("عدد المراحل", f"{stages} stages")
    e3.metric("قدرة المحرك", f"{esp_hp:.1f} HP")

# 4. منحنى IPR
with tabs[3]:
    st.subheader("📈 منحنى أداء التدفق (Vogel's IPR)")
    ic1, ic2 = st.columns(2)
    with ic1:
        p_res = st.number_input("ضغط المكمن (psi):", value=3000)
        p_wf = st.number_input("ضغط التدفق Pwf (psi):", value=2000)
    with ic2:
        q_test = st.number_input("معدل تدفق الاختبار (BPD):", value=1000)
        
    q_max = q_test / (1 - 0.2*(p_wf/p_res) - 0.8*((p_wf/p_res)**2)) if p_res > p_wf else q_test*1.5
    pwf_arr = np.linspace(0, p_res, 40)
    q_arr = q_max * (1 - 0.2*(pwf_arr/p_res) - 0.8*((pwf_arr/p_res)**2))
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(q_arr, pwf_arr, color='#0284c7', linewidth=2)
    ax.scatter([q_test], [p_wf], color='red', label=f'Test Point ({q_test} BPD)')
    ax.set_xlabel('Flow Rate Q (BPD)')
    ax.set_ylabel('Bottomhole Pressure Pwf (psi)')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)
    st.info(f"القدرة الإنتاجية القصوى للمكمن (AOF): **{q_max:,.0f} BPD**")

# 5. تحليل الملفات
with tabs[4]:
    st.subheader("📁 استيراد وتحليل ملفات البيانات (Excel & LAS)")
    f_type = st.radio("نوع الملف:", ["Excel / CSV", "LAS (Well Log)"], horizontal=True)
    
    if f_type == "Excel / CSV":
        up_file = st.file_uploader("اختر ملف إكسل أو CSV:", type=["xlsx", "csv"])
        if up_file:
            df = pd.read_csv(up_file) if up_file.name.endswith('.csv') else pd.read_excel(up_file)
            st.dataframe(df.head(5), use_container_width=True)
    else:
        up_las = st.file_uploader("اختر ملف LAS:", type=["las"])
        if up_las:
            try:
                las = lasio.read(up_las.read().decode("utf-8"))
                df_las = las.df().reset_index()
                st.success(f"تم تحميل سجل البئر: {las.well.WELL.value}")
                st.dataframe(df_las.head(5), use_container_width=True)
            except Exception as e:
                st.error(f"خطأ في قراءة ملف LAS: {e}")

# 6. المساعد الذكي
with tabs[5]:
    st.subheader("🤖 استشارات الذكاء الاصطناعي الهندسية")
    q_ai = st.text_area("اطرح سؤالك الهندسي هنا:", placeholder="مثال: كيف نعالج مشكلة الغاز الحر في مضخات ESP؟")
    
    if st.button("تحليل الأداء بواسطة Gemini 🧠", use_container_width=True):
        if not api_key:
            st.error("⚠️ يرجى إدخال مفتاح Gemini API في القائمة الجانبية أولاً.")
        elif not q_ai.strip():
            st.warning("⚠️ اكتب استفسارك أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                with st.spinner("جاري تحليل السؤال وإعداد التوصية الهندسية..."):
                    res = model.generate_content(f"أنت استشاري هندسة نفط وركّز على الإجابة بشكل علمي ومباشر: {q_ai}")
                    st.markdown("### 💡 التوصية الهندسية:")
                    st.write(res.text)
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")
