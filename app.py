import streamlit as st
import numpy as np
import pandas as pd

# -------------------------------------------------------------
# إعدادات الصفحة والواجهة
# -------------------------------------------------------------
st.set_page_config(
    page_title="تطبيق المنقب - تصميم الرفع الصناعي والذكاء الاصطناعي",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ برنامج المُنقّب - المدعوم بالذكاء الاصطناعي")
st.caption("منصة هندسة النفط الذكية: تصميم أجهزة الرفع الصناعي (SRP & ESP) والتحليل الذكي للآبار")

# -------------------------------------------------------------
# الشريط الجانبي (Sidebar)
# -------------------------------------------------------------
st.sidebar.header("🕹️ لوحة التحكم والوحدات")
app_mode = st.sidebar.radio(
    "اختر الوحدة المطلوبة:",
    [
        "⚙️ تصميم مضخات المكبس (SRP)",
        "⚡ تصميم المضخات الغاطسة (ESP)",
        "🤖 المساعد الهندسي الذكي (AI Assistant)"
    ]
)

# -------------------------------------------------------------
# 1. تصميم مضخات المكبس (SRP)
# -------------------------------------------------------------
if app_mode == "⚙️ تصميم مضخات المكبس (SRP)":
    st.header("⚙️ تصميم وتحديد مقاسات مضخة المكبس (SRP)")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 مدخلات البئر والتشغيل")
        depth = st.number_input("عمق البئر / المضخة (ft):", min_value=500, max_value=15000, value=5000, step=100)
        target_prod = st.number_input("معدل الإنتاج المطلوب (BPD):", min_value=10, max_value=3000, value=250, step=10)
        fluid_sg = st.number_input("الوزن النوعي للسائل (Fluid SG):", min_value=0.6, max_value=1.4, value=1.0, step=0.01)
        stroke_length = st.number_input("طول الشوط - Stroke Length (in):", min_value=24, max_value=200, value=86, step=2)
        spm = st.number_input("عدد الأشواط/دقيقة (SPM):", min_value=2, max_value=30, value=12, step=1)

    # الحسابات
    estimated_k = target_prod / (stroke_length * spm * 0.8)
    plunger_dia = np.sqrt(max(estimated_k, 0.001) / 0.1166)
    fluid_weight = 0.433 * fluid_sg * depth * (np.pi/4 * (plunger_dia**2))
    peak_rod_load = fluid_weight + (0.75 * depth)
    hydraulic_hp = (target_prod * depth * fluid_sg) / 135700
    motor_hp = hydraulic_hp / 0.55

    with col2:
        st.subheader("📊 النتائج التقديرية والتوصيات")
        m1, m2, m3 = st.columns(3)
        m1.metric("قطر المكبس", f"{plunger_dia:.2f} in")
        m2.metric("أقصى حمل قضبان", f"{peak_rod_load:,.0f} lbs")
        m3.metric("قدرة المحرك", f"{motor_hp:.1f} HP")
        
        st.info(f"""
        **ملخص تقرير التصميم:**
        * عمق الإنزال: **{depth:,} ft** | المعدل المستهدف: **{target_prod:,} BPD**
        * قطر المكبس الموصى به: **{plunger_dia:.2f} in**
        * سرعة التشغيل: **{spm} SPM** بشوط طوله **{stroke_length} in**
        """)

        # التقرير
        report_df = pd.DataFrame([{
            "العمق (ft)": depth, "معدل الإنتاج (BPD)": target_prod,
            "قطر المكبس (in)": round(plunger_dia, 2), "أقصى حمل (lbs)": round(peak_rod_load, 0),
            "قدرة المحرك (HP)": round(motor_hp, 1)
        }])
        csv_data = report_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل تقرير التصميم (CSV)", csv_data, f"SRP_Report_{depth}ft.csv", "text/csv")

    st.markdown("---")
    st.subheader("📈 العلاقة بين عمق البئر والقدرة الحصانية المطلوبة (HP)")
    depths = np.linspace(1000, 12000, 30)
    hps = [(target_prod * d * fluid_sg) / (135700 * 0.55) for d in depths]
    chart_data = pd.DataFrame({"العمق (ft)": depths, "القدرة (HP)": hps}).set_index("العمق (ft)")
    st.line_chart(chart_data)

# -------------------------------------------------------------
# 2. تصميم المضخات الغاطسة (ESP)
# -------------------------------------------------------------
elif app_mode == "⚡ تصميم المضخات الغاطسة (ESP)":
    st.header("⚡ تصميم وتحديد مقاسات المضخات الغاطسة (ESP)")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📥 مدخلات البئر والـ ESP")
        esp_depth = st.number_input("عمق إنزال المضخة (ft):", min_value=1000, max_value=15000, value=6000, step=100)
        esp_q = st.number_input("معدل التدفق المستهدف (BPD):", min_value=100, max_value=10000, value=1500, step=100)
        pip = st.number_input("ضغط السحب - Intake Pressure (psi):", min_value=50, max_value=2000, value=300, step=25)
        thp = st.number_input("ضغط رأس البئر - Wellhead Pressure (psi):", min_value=50, max_value=1000, value=150, step=25)
        esp_sg = st.number_input("الوزن النوعي للسائل (Fluid SG):", min_value=0.6, max_value=1.4, value=0.9, step=0.01)

    # الحسابات
    head_from_pressures = ((thp - pip) * 2.31) / esp_sg
    tdh = esp_depth + head_from_pressures
    stages = int(np.ceil(tdh / 25.0))
    esp_hp = (esp_q * tdh * esp_sg) / (135700 * 0.65)

    with col2:
        st.subheader("📊 نتائج تصميم المضخة (ESP Results)")
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي الـ TDH", f"{tdh:,.0f} ft")
        m2.metric("عدد المراحل", f"{stages} Stage")
        m3.metric("قدرة المحرك", f"{esp_hp:.1f} HP")
        
        st.success(f"""
        **ملخص تقرير ESP:**
        * ضخ **{esp_q:,} BPD** من عمق **{esp_depth:,} ft**
        * يتطلب مضخة بـ **{stages} مرحلة** لرفع السائل بمقدار **{tdh:,.0f} ft Head**
        * القدرة المطلوبة للمحرك الغاطس: **{esp_hp:.1f} HP**
        """)

        report_esp = pd.DataFrame([{
            "عمق المضخة (ft)": esp_depth, "التدفق (BPD)": esp_q,
            "الرأس الديناميكي TDH (ft)": round(tdh, 0), "عدد المراحل": stages,
            "قدرة المحرك (HP)": round(esp_hp, 1)
        }])
        csv_esp = report_esp.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل تقرير ESP (CSV)", csv_esp, f"ESP_Report_{esp_depth}ft.csv", "text/csv")

    st.markdown("---")
    st.subheader("📈 منحنى أداء المضخة (Head vs Flow Rate)")
    q_range = np.linspace(100, esp_q * 1.5, 30)
    head_curve = tdh * 1.3 - (0.3 * tdh * (q_range / esp_q)**2)
    esp_chart_data = pd.DataFrame({"معدل التدفق (BPD)": q_range, "ارتفاع الرفع - Head (ft)": head_curve}).set_index("معدل التدفق (BPD)")
    st.line_chart(esp_chart_data)

# -------------------------------------------------------------
# 3. المساعد الهندسي الذكي (AI Petroleum Assistant)
# -------------------------------------------------------------
else:
    st.header("🤖 المساعد الهندسي الذكي (AI Petroleum Assistant)")
    st.write("احصل على توصيات ذكية واستشارات هندسية فورية حول مشاكل الإنتاج والرفع الصناعي.")
    
    st.markdown("---")
    user_query = st.text_area("✍️ اكتب استفسارك الهندسي هنا (مثال: متى أختار ESP بدلاً من SRP؟ أو ما أسباب انخفاض كفاءة المضخة؟):")
    
    if st.button("🧠 تحليل واستشارة الذكاء الاصطناعي"):
        if user_query.strip() != "":
            st.subheader("💡 التوصية الهندسية من المساعد الذكي:")
            
            # محاكاة تحليل ذكي بالاعتماد على الكلمات المفتاحية
            query_lower = user_query.lower()
            if "esp" in query_lower or "غاطس" in query_lower:
                st.info("""
                **تحليل نظام ESP:**
                * **الاستخدام الأنسب:** الآبار ذات الإنتاج العالي جداً (> 1000 BPD) والعمق المتوسط إلى العالي.
                * **التحديات:** حساسة جداً لوجود الغاز الحر بنسبة عالية (> 20%) والرمال (Sand production).
                * **توصية:** يُفضل استخدام الفرازة الغازية (Gas Separator) قبل سحب المضخة إذا كان البئر يحتوي على غاز مصاحب.
                """)
            elif "srp" in query_lower or "مكبس" in query_lower:
                st.info("""
                **تحليل نظام SRP:**
                * **الاستخدام الأنسب:** الآبار ذات الإنتاج المنخفض إلى المتوسط (< 1000 BPD) واللزوجة العالية.
                * **التحديات:** تآكل قضبان الشفط (Rod wear) في الآبار المائلة.
                * **توصية:** نظام ممتاز واقتصادي جداً للآبار القديمة والمتقادمة (Mature Fields).
                """)
            else:
                st.success(f"""
                **التوصية العامة للبئر:**
                * تم تحليل استفسارك: "{user_query}"
                * في اختيار أجهزة الرفع الصناعي، القاعدة الأساسية تعتمد على: (معدل الإنتاج المطلوب، نسبة الغاز للنفط GOR، ونسبة الماء BS&W).
                * يُنصح بضبط ضغط السحب (PIP) ليكون أعلى من ضغط نقطة الفقاعة (Bubble Point Pressure) لمنع انفصال الغاز داخل المضخة.
                """)
        else:
            st.warning("يرجى كتابة الاستفسار أولاً.")
