import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import lasio
import google.generativeai as genai

# ---------------------------------------------------------
# إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="Al-Munaqqib Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# اختيار اللغة في القائمة الجانبية
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings / الإعدادات")
    lang = st.selectbox("🌐 اختر اللغة / Select Language", ["العربية", "English"])
    api_key = st.text_input("Gemini API Key:", type="password")
    st.divider()
    st.info("💡 **منصة المُنقّب الهندسية v4.0**\nنظام احترافي لتصميم الرفع الصناعي، تحليل المكامن، والتقييم الاقتصادي.")

# ---------------------------------------------------------
# قاموس اللغات والترجمة
# ---------------------------------------------------------
T = {
    "العربية": {
        "title": "⚡ منصة المُنقّب الهندسية المتكاملة",
        "subtitle": "نظام هندسي متقدم لترشيح وتصميم أجهزة الرفع، تحليل المكامن، التقييم الاقتصادي، واستشارات الذكاء الاصطناعي",
        "tabs": ["🎯 الترشيح الذكي والـ CAPEX", "⚙️ تصميم SRP", "⚡ تصميم ESP", "📈 منحنى IPR", "📁 تحليل الملفات", "🤖 المساعد الذكي"],
        "screening_title": "🎯 نظام الاختيار والترشيح الآلي المعياري (Smart Selector)",
        "target_prod": "الإنتاج المستهدف (BPD):",
        "depth": "العمق العمودي (ft):",
        "gor": "نسبة الغاز للنفط GOR (scf/stb):",
        "visc": "اللزوجة (cP):",
        "btn_screen": "ترشيح النظام الأمثل وحساب التكاليف 🔍",
        "srp_title": "⚙️ تصميم مضخات المكبس (Sucker Rod Pump)",
        "pump_depth": "عمق المضخة (ft):",
        "stroke_len": "طول الشوط (in):",
        "spm": "عدد الأشواط (SPM):",
        "p_dia": "قطر المكبس",
        "peak_load": "أقصى حمل (Peak Load)",
        "motor_hp": "قدرة المحرك",
        "esp_title": "⚡ تصميم المضخات الكهربائية الغاطسة (ESP)",
        "head_stg": "الرفع لكل مرحلة (ft):",
        "p_surf": "الضغط السطحي (psi):",
        "tdh": "إجمالي الرفع (TDH)",
        "stages": "عدد المراحل",
        "ipr_title": "📈 منحنى أداء التدفق (Vogel's IPR)",
        "p_res": "ضغط المكمن (psi):",
        "p_wf": "ضغط التدفق Pwf (psi):",
        "q_test": "معدل تدفق الاختبار (BPD):",
        "aof": "القدرة الإنتاجية القصوى للمكمن (AOF):",
        "ai_title": "🤖 استشارات الذكاء الاصطناعي الهندسية",
        "ai_prompt": "اطرح سؤالك الهندسي أو استفسارك هنا:",
        "btn_ai": "تحليل الأداء بواسطة Gemini 🧠",
        "ai_res": "💡 التوصية الهندسية:",
        "report_title": "📄 تصدير التقرير الهندسي والاقتصادي",
        "btn_download": "تنزيل التقرير الهندسي الشامل (TXT) 📥"
    },
    "English": {
        "title": "⚡ Al-Munaqqib Engineering Suite",
        "subtitle": "Advanced engineering system for artificial lift selection, reservoir analysis, economics, and AI",
        "tabs": ["🎯 Smart Screening & CAPEX", "⚙️ SRP Design", "⚡ ESP Design", "📈 IPR Curve", "📁 File Analysis", "🤖 AI Assistant"],
        "screening_title": "🎯 Advanced Automated System Screening & Selection",
        "target_prod": "Target Production (BPD):",
        "depth": "Vertical Depth (ft):",
        "gor": "Gas-Oil Ratio GOR (scf/stb):",
        "visc": "Viscosity (cP):",
        "btn_screen": "Screen Optimal System & Economics 🔍",
        "srp_title": "⚙️ Sucker Rod Pump (SRP) Design",
        "pump_depth": "Pump Depth (ft):",
        "stroke_len": "Stroke Length (in):",
        "spm": "Strokes Per Minute (SPM):",
        "p_dia": "Plunger Diameter",
        "peak_load": "Peak Load",
        "motor_hp": "Motor Horsepower",
        "esp_title": "⚡ Electric Submersible Pump (ESP) Design",
        "head_stg": "Head per Stage (ft):",
        "p_surf": "Surface Pressure (psi):",
        "tdh": "Total Dynamic Head (TDH)",
        "stages": "Total Stages",
        "ipr_title": "📈 Inflow Performance Relationship (Vogel's IPR)",
        "p_res": "Reservoir Pressure (psi):",
        "p_wf": "Flowing BHP (psi):",
        "q_test": "Test Flow Rate (BPD):",
        "aof": "Absolute Open Flow (AOF):",
        "ai_title": "🤖 AI Engineering Consultation",
        "ai_prompt": "Enter your engineering query here:",
        "btn_ai": "Analyze via Gemini 🧠",
        "ai_res": "💡 Engineering Recommendation:",
        "report_title": "📄 Export Engineering & Economic Report",
        "btn_download": "Download Comprehensive Engineering Report (TXT) 📥"
    }
}

t = T[lang]

# ---------------------------------------------------------
# الواجهة الرئيسية
# ---------------------------------------------------------
st.title(t["title"])
st.caption(t["subtitle"])

tabs = st.tabs(t["tabs"])

# متغيرات عامة لحفظ التقرير
report_data = {}

# 1. الترشيح الذكي وتقييم التكاليف الاقتصادية (CAPEX / OPEX)
with tabs[0]:
    st.subheader(t["screening_title"])
    c1, c2 = st.columns(2)
    with c1:
        q_target = st.number_input(t["target_prod"], value=2500, step=100)
        depth_ft = st.number_input(t["depth"], value=7000, step=500)
    with c2:
        gor = st.number_input(t["gor"], value=500, step=50)
        visc = st.number_input(t["visc"], value=15.0, step=1.0)
        
    recommended_system = "SRP"
    capex_est = 0
    opex_est = 0
    
    if st.button(t["btn_screen"], use_container_width=True):
        # خوارزمية الترشيح المعيارية الحقيقية
        if visc > 300:
            recommended_system = "PCP (Progressive Cavity Pump) - ملائم جداً للزوجة العالية"
            capex_est, opex_est = 65000, 120
        elif gor > 1500 and depth_ft > 10000:
            recommended_system = "Gas Lift System - الأنسب للغاز العالي والأعماق الكبيرة"
            capex_est, opex_est = 90000, 150
        elif q_target > 3500:
            recommended_system = "ESP (Electric Submersible Pump) - الأفضل لمعدلات الإنتاج العالية"
            capex_est, opex_est = 120000, 250
        else:
            recommended_system = "SRP (Sucker Rod Pump) - الخيار الاقتصادي الأمثل للأعماق والإنتاج المتوسط"
            capex_est, opex_est = 45000, 80

        st.success(f"📌 **التوصية الهندسية:** {recommended_system}")
        
        # عرض التقييم الاقتصادي
        st.markdown("### 💰 التقييم الاقتصادي المبدئي (Economics Estimation)")
        ec1, ec2 = st.columns(2)
        ec1.metric("CAPEX (التكلفة الأولية التقديرية)", f"${capex_est:,.0f}")
        ec2.metric("OPEX (تكلفة التشغيل اليومية)", f"${opex_est:,.0f} / day")
        
        report_data['screening'] = f"Target Production: {q_target} BPD, Depth: {depth_ft} ft, GOR: {gor}, Viscosity: {visc} cP \n-> Recommended System: {recommended_system} \n-> Estimated CAPEX: ${capex_est:,.0f}, OPEX: ${opex_est}/day"

# 2. تصميم SRP
with tabs[1]:
    st.subheader(t["srp_title"])
    col1, col2 = st.columns(2)
    with col1:
        d_srp = st.number_input(t["pump_depth"], value=5000, key="dsrp")
        q_srp = st.number_input(t["target_prod"], value=300, key="qsrp")
    with col2:
        s_len = st.number_input(t["stroke_len"], value=86, key="slen")
        spm = st.number_input(t["spm"], value=12, key="spm")
        
    p_size = np.sqrt(q_srp / (0.1166 * s_len * spm * 0.8)) if (s_len * spm) > 0 else 1.5
    peak_l = (0.433 * d_srp * (np.pi * (p_size/2)**2)) + (d_srp * 1.6)
    hp_req = (peak_l * s_len * spm) / 375000 + 5
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric(t["p_dia"], f"{p_size:.2f} in")
    m2.metric(t["peak_load"], f"{peak_l:,.0f} lbs")
    m3.metric(t["motor_hp"], f"{hp_req:.1f} HP")
    
    report_data['srp'] = f"SRP Design -> Depth: {d_srp} ft, Plunger Size: {p_size:.2f} in, Peak Load: {peak_l:,.0f} lbs, Motor HP: {hp_req:.1f} HP"

# 3. تصميم ESP
with tabs[2]:
    st.subheader(t["esp_title"])
    col1, col2 = st.columns(2)
    with col1:
        d_esp = st.number_input(t["pump_depth"], value=7500, key="desp")
        q_esp = st.number_input(t["target_prod"], value=4000, key="qesp")
    with col2:
        h_stg = st.number_input(t["head_stg"], value=25, key="hstg")
        p_surf = st.number_input(t["p_surf"], value=200, key="psurf")
        
    tdh = d_esp + (p_surf * 2.31)
    stages = int(tdh / h_stg) if h_stg > 0 else 100
    esp_hp = (q_esp * tdh) / 135000
    
    st.divider()
    e1, e2, e3 = st.columns(3)
    e1.metric(t["tdh"], f"{tdh:,.0f} ft")
    e2.metric(t["stages"], f"{stages}")
    e3.metric(t["motor_hp"], f"{esp_hp:.1f} HP")
    
    report_data['esp'] = f"ESP Design -> Depth: {d_esp} ft, TDH: {tdh:,.0f} ft, Stages: {stages}, Motor HP: {esp_hp:.1f} HP"

# 4. منحنى IPR
with tabs[3]:
    st.subheader(t["ipr_title"])
    ic1, ic2 = st.columns(2)
    with ic1:
        p_res = st.number_input(t["p_res"], value=3000)
        p_wf = st.number_input(t["p_wf"], value=2000)
    with ic2:
        q_test = st.number_input(t["q_test"], value=1000)
        
    q_max = q_test / (1 - 0.2*(p_wf/p_res) - 0.8*((p_wf/p_res)**2)) if p_res > p_wf else q_test*1.5
    pwf_arr = np.linspace(0, p_res, 40)
    q_arr = q_max * (1 - 0.2*(pwf_arr/p_res) - 0.8*((pwf_arr/p_res)**2))
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(q_arr, pwf_arr, color='#0284c7', linewidth=2, label="Vogel's IPR Curve")
    ax.scatter([q_test], [p_wf], color='red', s=70, label=f'Operating Test Point ({q_test} BPD)')
    ax.set_xlabel('Flow Rate Q (BPD)')
    ax.set_ylabel('Bottomhole Pressure Pwf (psi)')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)
    st.info(f"{t['aof']} **{q_max:,.0f} BPD**")
    
    report_data['ipr'] = f"IPR Analysis -> Reservoir Pressure: {p_res} psi, Test Rate: {q_test} BPD, AOF: {q_max:,.0f} BPD"

# 5. تحليل الملفات
with tabs[4]:
    st.subheader("📁 " + ("تحليل الملفات والسجلات" if lang == "العربية" else "File & Log Analysis"))
    up_file = st.file_uploader("Upload Excel / CSV / LAS", type=["xlsx", "csv", "las"])
    if up_file:
        st.success(f"File uploaded successfully: {up_file.name}")
        report_data['file'] = f"Uploaded File: {up_file.name}"

# 6. المساعد الذكي Gemini
with tabs[5]:
    st.subheader(t["ai_title"])
    q_ai = st.text_area(t["ai_prompt"])
    
    if st.button(t["btn_ai"], use_container_width=True):
        if not api_key:
            st.error("⚠️ يرجى أدخال مفتاح Gemini API في القائمة الجانبية أولاً." if lang == "العربية" else "⚠️ Please provide Gemini API Key in the sidebar.")
        elif q_ai.strip():
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("جاري التحليل الهندسي..." if lang == "العربية" else "Analyzing..."):
                    lang_prompt = "أجب باللغة العربية كخبير هندسة إنتاج بترول." if lang == "العربية" else "Answer in English as a petroleum production expert."
                    res = model.generate_content(f"{lang_prompt} {q_ai}")
                    st.markdown(f"### {t['ai_res']}")
                    st.write(res.text)
                    report_data['ai'] = f"AI Query: {q_ai} \n Answer: {res.text}"
            except Exception as e:
                st.error(f"Error: {e}")

# ---------------------------------------------------------
# قسم تصدير التقرير الهندسي والاقتصادي الشامل
# ---------------------------------------------------------
st.divider()
st.subheader(t["report_title"])

report_content = f"""
==================================================
        AL-MUNAIQQIB ENGINEERING PLATFORM REPORT
        منصة المُنقّب الهندسية - التقرير الشامل
==================================================

1. SMART SCREENING & ECONOMIC EVALUATION:
{report_data.get('screening', 'Not evaluated yet.')}

2. SUCKER ROD PUMP (SRP) DESIGN:
{report_data.get('srp', 'Not calculated yet.')}

3. ELECTRIC SUBMERSIBLE PUMP (ESP) DESIGN:
{report_data.get('esp', 'Not calculated yet.')}

4. IPR & RESERVOIR PERFORMANCE:
{report_data.get('ipr', 'Not calculated yet.')}

5. FILE & AI CONSULTATION:
{report_data.get('file', 'No files uploaded.')}
{report_data.get('ai', 'No AI queries performed.')}

==================================================
Generated by Al-Munaqqib Suite | Petroleum Engineering
==================================================
"""

st.download_button(
    label=t["btn_download"],
    data=report_content,
    file_name="Al_Munaqqib_Comprehensive_Report.txt",
    mime="text/plain",
    use_container_width=True
)
