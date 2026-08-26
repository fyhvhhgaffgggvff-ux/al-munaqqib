import streamlit as st
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="تطبيق المنقب - تصميم الرفع الصناعي", layout="wide")

st.title("⚓ وحدة تصميم أجهزة الرفع الصناعي (Artificial Lift Sizing)")
st.caption("برنامج المُنقّب - حساب وتحديد مقاسات مضخات المكبس (SRP) والمضخات الغاطسة (ESP)")

# شريط اختيارات نوع المضخة
pump_type = st.sidebar.selectbox("اختر نوع نظام الرفع الصناعي:", ["مضخات المكبس (Sucker Rod Pump)", "المضخات الغاطسة الكهربائية (ESP)"])

if pump_type == "مضخات المكبس (Sucker Rod Pump)":
    st.header("⚙️ تصميم وتحديد مقاسات مضخة المكبس (SRP)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 المدخلات الهندسية (Well Inputs)")
        depth = st.number_input("عمق البئر أو المضخة (ft):", min_value=500, max_value=15000, value=5000, step=100)
        target_prod = st.number_input("معدل الإنتاج المطلوب (BPD):", min_value=10, max_value=3000, value=250, step=10)
        fluid_sg = st.number_input("الوزن النوعي للسائل (Fluid SG):", min_value=0.6, max_value=1.2, value=1.0, step=0.01)
        stroke_length = st.number_input("طول الشوط - Stroke Length (in):", min_value=24, max_value=200, value=86, step=2)
        spm = st.number_input("عدد الأشواط/دقيقة (SPM):", min_value=2, max_value=30, value=12, step=1)

    # الحسابات
    estimated_k = target_prod / (stroke_length * spm * 0.8)
    plunger_dia = np.sqrt(estimated_k / 0.1166)
    fluid_weight = 0.433 * fluid_sg * depth * (np.pi/4 * (plunger_dia**2))
    peak_rod_load = fluid_weight + (0.75 * depth)
    hydraulic_hp = (target_prod * depth * fluid_sg) / 135700
    motor_hp = hydraulic_hp / 0.55

    with col2:
        st.subheader("📊 النتائج والتوصيات")
        st.metric("قطر المكبس المقترح (Plunger Size)", f"{plunger_dia:.2f} in")
        st.metric("أقصى حمل متوقع على القضبان (Peak Rod Load)", f"{peak_rod_load:,.0f} lbs")
        st.metric("القدرة الحصانية للمحرك (Required Motor HP)", f"{motor_hp:.1f} HP")
        
        st.info(f"""
        **ملخص التصميم:**
        * للوصول لإنتاج **{target_prod} BPD** عند عمق **{depth} ft**.
        * استخدام مكبس بقطر **{plunger_dia:.2f} بوصة**.
        * سرعة الضخ **{spm} SPM** بشوط **{stroke_length} بوصة**.
        """)

else:
    st.header("⚡ تصميم وتحديد مقاسات المضخات الغاطسة (ESP)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 المدخلات الهندسية (ESP Inputs)")
        esp_depth = st.number_input("عمق إنزال المضخة - Pump Depth (ft):", min_value=1000, max_value=15000, value=6000, step=100)
        esp_q = st.number_input("معدل التدفق المستهدف - Flow Rate (BPD):", min_value=100, max_value=10000, value=1500, step=100)
        pip = st.number_input("ضغط السحب - Intake Pressure (psi):", min_value=50, max_value=2000, value=300, step=25)
        thp = st.number_input("ضغط رأس البئر المطلوب - Wellhead Pressure (psi):", min_value=50, max_value=1000, value=150, step=25)
        esp_sg = st.number_input("الوزن النوعي للسائل (Fluid SG):", min_value=0.6, max_value=1.2, value=0.9, step=0.01)

    # حسابات ESP
    # 1. Total Dynamic Head (TDH)
    head_from_depth = esp_depth
    head_from_pressures = ((thp - pip) * 2.31) / esp_sg
    tdh = head_from_depth + head_from_pressures
    
    # 2. Number of Stages (افتقاض متوسط رفع المرحلة 25 قدم)
    avg_head_per_stage = 25.0
    stages = int(np.ceil(tdh / avg_head_per_stage))
    
    # 3. Motor HP Calculation
    # HP = (Q * TDH * SG) / (135700 * Efficiency) -> بفرض كفاءة 65%
    esp_hp = (esp_q * tdh * esp_sg) / (135700 * 0.65)

    with col2:
        st.subheader("📊 نتائج تصميم الـ ESP")
        st.metric("إجمالي الرأس الديناميكي (Total Dynamic Head - TDH)", f"{tdh:,.0f} ft")
        st.metric("عدد مراحل المضخة المطلوبة (Estimated Stages)", f"{stages} Stage")
        st.metric("قدرة المحرك المطلوب (Required Motor HP)", f"{esp_hp:.1f} HP")
        
        st.success(f"""
        **ملخص تصميم ESP:**
        * ضخ **{esp_q} BPD** من عمق **{esp_depth} ft**.
        * يلزم مضخة بـ **{stages} مرحلة** لرفع السائل بـ **{tdh:,.0f} قدم من الـ Head**.
        * قدرة المحرك الكهربائي الغاطس المطلوبة: **{esp_hp:.1f} HP**.
        """)
