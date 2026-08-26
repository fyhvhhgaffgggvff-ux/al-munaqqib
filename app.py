import streamlit as st
import numpy as np
import pandas as pd
import google.generativeai as genai

# ---------------------------------------------------------
# إعدادات الصفحة والواجهة
# ---------------------------------------------------------
st.set_page_config(
    page_title="برنامج المُنقّب - تصميم أجهزة الرفع الصناعي",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ برنامج المُنقّب - المساعد الهندسي الذكي")
st.caption("برنامج حساب وتصميم أجهزة الرفع الصناعي والذكاء الاصطناعي")

# ---------------------------------------------------------
# الشريط الجانبي (Sidebar)
# ---------------------------------------------------------
st.sidebar.header("🔑 إعدادات الذكاء الاصطناعي")
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

st.sidebar.header("⚙️ خيارات النظام")
lift_type = st.sidebar.selectbox(
    "اختر نوع نظام الرفع الصناعي:",
    ["مضخات المكبس (Sucker Rod Pump)", "(ESP) المضخات الغاطسة الكهربائية"]
)

# ---------------------------------------------------------
# الواجهة الأولى: مضخات المكبس (Sucker Rod Pump)
# ---------------------------------------------------------
if lift_type == "مضخات المكبس (Sucker Rod Pump)":
    st.header("⚙️ حسابات وتصميم مضخات المكبس (SRP)")
    
    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        depth = st.number_input("عمق البئر (ft):", min_value=1000, max_value=15000, value=5000, step=500)
        flow_rate = st.number_input("(BPD) معدل الإنتاج المطلوب:", min_value=10, max_value=2000, value=250, step=10)
        fluid_sg = st.number_input("(Fluid SG) الفيزياء النوعية للسائل:", min_value=0.5, max_value=1.5, value=1.00, step=0.05)
        
    with col_in2:
        stroke_length = st.number_input("طول الشوط - Stroke Length (in):", min_value=24, max_value=200, value=86, step=2)
        spm = st.number_input("عدد الأشواط/دقيقة (Strokes Per Minute - SPM):", min_value=4, max_value=30, value=12, step=1)

    # حسابات هندسية تقريبية لـ SRP
    plunger_size = np.sqrt(flow_rate / (0.1166 * stroke_length * spm * 0.8)) if (stroke_length * spm) > 0 else 1.5
    fluid_weight = 0.433 * fluid_sg * depth * (np.pi * (plunger_size / 2)**2)
    peak_rod_load = fluid_weight + (depth * 1.6)
    required_hp = (peak_rod_load * stroke_length * spm) / 375000 + 5

    st.divider()
    st.subheader("📊 النتائج والتوصيات الموصى بها")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("قطر المكبس المقترح (Plunger Size)", f"{plunger_size:.2f} in")
    res_col2.metric("أقصى حمل متوقع (Peak Rod Load)", f"{peak_rod_load:,.0f} lbs")
    res_col3.metric("القدرة الحصانية للمحرك (Required Motor HP)", f"{required_hp:.1f} HP")

    st.info(f"""
    **ملخص التصميم:**
    * عند عمق **{depth} ft** للوصول للإصدار المطلوب **{flow_rate} BPD**.
    * يُوصى باستخدام مضخة بمكبس قطر **{plunger_size:.2f} in** مع شوط طوله **{stroke_length} in** وتشغيل المضخة بمعدل **{spm} SPM**.
    """)

# ---------------------------------------------------------
# الواجهة الثانية: المضخات الغاطسة (ESP)
# ---------------------------------------------------------
else:
    st.header("⚡ حسابات وتصميم المضخات الغاطسة (ESP)")
    
    col_esp1, col_esp2 = st.columns(2)
    with col_esp1:
        depth = st.number_input("عمق البئر (ft):", min_value=1000, max_value=20000, value=7000, step=500)
        flow_rate = st.number_input("(BPD) معدل الإنتاج المطلوب:", min_value=500, max_value=15000, value=3500, step=100)
    
    with col_esp2:
        head_per_stage = st.number_input("الرفع لكل مرحلة Head/Stage (ft):", min_value=10, max_value=100, value=25, step=5)
        p_disp = st.number_input("الضغط المطلوب عند السطح (psi):", min_value=50, max_value=1000, value=200, step=25)

    # حسابات ESP
    total_head = depth + (p_disp * 2.31)
    stages = int(total_head / head_per_stage) if head_per_stage > 0 else 100
    esp_hp = (flow_rate * total_head) / 135000

    st.divider()
    st.subheader("📊 النتائج والتوصيات الموصى بها (ESP)")
    
    e_col1, e_col2, e_col3 = st.columns(3)
    e_col1.metric("إجمالي الرفع الهيدروليكي (Total Head)", f"{total_head:,.0f} ft")
    e_col2.metric("عدد مراحل المضخة (Stages Required)", f"{stages} stage")
    e_col3.metric("قدرة المحرك المطلوب (Motor HP)", f"{esp_hp:.1f} HP")

st.divider()

# ---------------------------------------------------------
# قسم المساعد الهندسي الذكي (Gemini AI)
# ---------------------------------------------------------
st.subheader("🤖 المساعد الهندسي الذكي (Gemini AI)")

user_query = st.text_area(
    "اكتب استفسارك الهندسي هنا (مثال: ما أسباب انخفاض كفاءة المضخة؟ أو كيف أختار قطر المكبس المناسب؟):",
    height=100
)

if st.button("تحليل واستشارة الذكاء الاصطناعي 🧠"):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح Gemini API في الشريط الجانبي أولاً لتفعيل هذه الميزة!")
    elif not user_query.strip():
        st.warning("⚠️ يرجى كتابة سؤالك قبل الضغط على الزر.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            أنت خبير واستشاري في هندسة النفط ومتخصص في أجهزة الرفع الصناعي (Artificial Lift Systems).
            نوع النظام المختار حالياً: {lift_type}
            بيانات البئر المدخلة: العمق = {depth} ft، معدل الإنتاج = {flow_rate} BPD.
            
            سؤال المستخدم:
            "{user_query}"
            
            قدم إجابة هندسية دقيقة، مختصرة، ومباشرة في نقاط موجهة لمهندس الإنتاج.
            """
            
            with st.spinner("جاري تحليل السؤال وتوليد التوصية الهندسية..."):
                response = model.generate_content(prompt)
                st.markdown("### 💡 التوصية الهندسية من المساعد الذكي:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
