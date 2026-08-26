import streamlit as st
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="تطبيق المنقب - تصميم الرفع الصناعي", layout="wide")

st.title("⚓ وحدة تصميم أجهزة الرفع الصناعي (Artificial Lift Sizing)")
st.caption("برنامج المُنقّب الهندي - حساب وتحديد مقاسات مضخات المكبس (SRP) والمضخات الغاطسة (ESP)")

# إضافة شريط لاختيار نوع المضخة
pump_type = st.sidebar.selectbox("اختر نوع نظام الرفع الصناعي:", ["مضخات المكبس (Sucker Rod Pump)", "المضخات الغاطسة الكهربائية (ESP)"])

if pump_type == "مضخات المكبس (Sucker Rod Pump)":
    st.header("⚙️ تصميم وتحديد مقاسات مضخة المكبس (SRP)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 المدخلات الهندسية (Well Inputs)")
        depth = st.number_input("عمق البئر أو المضخة (ft):", min_value=500, max_value=15000, value=5000, step=100)
        target_prod = st.number_input("معدل الإنتاج المطلوب (BPD):", min_value=10, max_value=3000, value=250, step=10)
        fluid_sg = st.number_input("الفيزياء النوعية للسائل (Fluid SG):", min_value=0.6, max_value=1.2, value=1.0, step=0.01)
        stroke_length = st.number_input("طول الشوط - Stroke Length (in):", min_value=24, max_value=200, value=86, step=2)
        spm = st.number_input("عدد الأشواط/دقيقة (Strokes Per Minute - SPM):", min_value=2, max_value=30, value=12, step=1)

    # حسابات معيارية مصغرة
    # 1. القطر التقديري للمكبس بناءً على الإنتاج وطول الشوط
    # K Constant approximation for Pump Displacement: PD = K * S * SPM
    # Plunger constant K = 0.1166 * D^2
    estimated_k = target_prod / (stroke_length * spm * 0.8) # بفرض كفاءة 80%
    plunger_dia = np.sqrt(estimated_k / 0.1166)
    
    # 2. حساب الوزن السائل الحجمي وحمل القضبان (Fluid Weight & Peak Rod Load)
    fluid_weight = 0.433 * fluid_sg * depth * (np.pi/4 * (plunger_dia**2))
    peak_rod_load = fluid_weight + (0.75 * depth) # معادلة تقريبية لحمل قضبان الشفط
    
    # 3. حساب القدرة الحصانية المطلوبة (Hydraulic Horsepower)
    hydraulic_hp = (target_prod * depth * fluid_sg) / 135700
    motor_hp = hydraulic_hp / 0.55 # افتراض كفاءة ميكانيكية متكاملة 55%

    with col2:
        st.subheader("📊 النتائج والتوصيات الموصى بها")
        st.metric("قطر المكبس المقترح (Plunger Size)", f"{plunger_dia:.2f} in")
        st.metric("أقصى حمل متوقع على القضبان (Peak Rod Load)", f"{peak_rod_load:,.0f} lbs")
        st.metric("القدرة الحصانية للمحرك (Required Motor HP)", f"{motor_hp:.1f} HP")
        
        st.info(f"""
        **ملخص التصميم:**
        * للوصول للإنتاج المطلوب **{target_prod} BPD** عند عمق **{depth} ft**.
        * يُوصى باستخدام مضخة بمكبس قطر **{plunger_dia:.2f} بوصة**.
        * تشغيل المضخة بمعدل **{spm} SPM** مع شوط طوله **{stroke_length} in**.
        """)

else:
    st.header("⚡ تصميم المضخات الغاطسة الكهربائية (ESP)")
    st.write("سيتم تفعيل معادلات الـ ESP التفصيلية في التحديث القادم...")
