import streamlit as st
import numpy as np
import pandas as pd
import google.generativeai as genai

# ---------------------------------------------------------
# إعدادات الصفحة والثيم العام
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة المُنقّب الهندسية",
    page_icon="⚡",
    layout="wide"
)

# تنسيق البطاقات والمظهر
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #334155;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 14px;
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ منصة المُنقّب للهندسة والرفع الصناعي")
st.caption("أداة متكاملة لتصميم أجهزة الرفع الصناعي مع ميزة استخراج البيانات الذكية")

# ---------------------------------------------------------
# الشريط الجانبي
# ---------------------------------------------------------
st.sidebar.header("🔑 إعدادات النظام")
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

# ---------------------------------------------------------
# الواجهة الرئيسية باستخدام التبويبات
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["⚙️ تصميم SRP واستخراج البيانات", "⚡ تصميم ESP", "🤖 المساعد الهندسي الذكي"])

# --- التبويب الأول: مضخات المكبس مع استيراد الملفات ---
with tab1:
    st.subheader("حسابات مضخات المكبس (Sucker Rod Pump)")
    
    # خيار تحديد طريقة إدخال البيانات
    data_mode = st.radio("اختر طريقة إدخال البيانات:", ["إدخال يدوي ✍️", "رفع ملف بيانات (Excel / CSV) 📁"], horizontal=True)
    
    # قيم افتراضية
    depth_val = 5000
    flow_val = 250
    
    if data_mode == "رفع ملف بيانات (Excel / CSV) 📁":
        uploaded_file = st.file_uploader("اختر ملف الإكسل أو CSV الخاص بالبئر:", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success("تم رفع الملف واستخراج البيانات بنجاح! 📊")
                st.dataframe(df.head(3), use_container_width=True) # عرض أول 3 أعمدة
                
                # استخراج القيم تلقائياً إذا كانت الأعمدة موجودة في الملف
                if 'Depth' in df.columns:
                    depth_val = int(df['Depth'].iloc[0])
                if 'FlowRate' in df.columns:
                    flow_val = int(df['FlowRate'].iloc[0])
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        depth_srp = st.number_input("عمق البئر (ft):", min_value=1000, max_value=15000, value=depth_val, step=500, key="d_srp")
        flow_srp = st.number_input("معدل الإنتاج المطلوب (BPD):", min_value=10, max_value=2000, value=flow_val, step=10, key="f_srp")
        sg_srp = st.number_input("الكثافة النوعية للسائل (Fluid SG):", min_value=0.5, max_value=1.5, value=1.00, step=0.05, key="sg_srp")
        
    with col2:
        stroke = st.number_input("طول الشوط (Stroke Length - in):", min_value=24, max_value=200, value=86, step=2)
        spm = st.number_input("عدد الأشواط/دقيقة (SPM):", min_value=4, max_value=30, value=12, step=1)

    # المعادلات
    plunger_size = np.sqrt(flow_srp / (0.1166 * stroke * spm * 0.8)) if (stroke * spm) > 0 else 1.5
    fluid_weight = 0.433 * sg_srp * depth_srp * (np.pi * (plunger_size / 2)**2)
    peak_rod_load = fluid_weight + (depth_srp * 1.6)
    required_hp = (peak_rod_load * stroke * spm) / 375000 + 5

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">قطر المكبس المقترح</div>
            <div class="metric-value">{plunger_size:.2f} in</div>
        </div>''', unsafe_allow_html=True)
        
    with c2:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">أقصى حمل متوقع (Peak Load)</div>
            <div class="metric-value">{peak_rod_load:,.0f} lbs</div>
        </div>''', unsafe_allow_html=True)
        
    with c3:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">القدرة الحصانية للمحرك</div>
            <div class="metric-value">{required_hp:.1f} HP</div>
        </div>''', unsafe_allow_html=True)

# --- التبويب الثاني: المضخات الغاطسة ---
with tab2:
    st.subheader("حسابات المضخات الكهربائية الغاطسة (ESP)")
    col1, col2 = st.columns(2)
    with col1:
        depth_esp = st.number_input("عمق البئر (ft):", min_value=1000, max_value=20000, value=7000, step=500, key="d_esp")
        flow_esp = st.number_input("معدل الإنتاج المطلوب (BPD):", min_value=500, max_value=15000, value=3500, step=100, key="f_esp")
    
    with col2:
        head_stage = st.number_input("الرفع لكل مرحلة Head/Stage (ft):", min_value=10, max_value=100, value=25, step=5)
        p_surface = st.number_input("الضغط السطحي المطلوب (psi):", min_value=50, max_value=1000, value=200, step=25)

    total_head = depth_esp + (p_surface * 2.31)
    stages = int(total_head / head_stage) if head_stage > 0 else 100
    esp_hp = (flow_esp * total_head) / 135000

    st.markdown("<br>", unsafe_allow_html=True)
    ec1, ec2, ec3 = st.columns(3)
    
    with ec1:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">إجمالي الرفع (Total Head)</div>
            <div class="metric-value">{total_head:,.0f} ft</div>
        </div>''', unsafe_allow_html=True)
        
    with ec2:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">عدد مراحل المضخة</div>
            <div class="metric-value">{stages} stages</div>
        </div>''', unsafe_allow_html=True)
        
    with ec3:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-label">قدرة المحرك المطلوبة</div>
            <div class="metric-value">{esp_hp:.1f} HP</div>
        </div>''', unsafe_allow_html=True)

# --- التبويب الثالث: المساعد الذكي ---
with tab3:
    st.subheader("🤖 استشارات الهندسة والرفع الصناعي")
    user_query = st.text_area("اطرح استفسارك الهندسي هنا:", height=120)

    if st.button("تحليل واستشارة الذكاء الاصطناعي 🧠", use_container_width=True):
        if not api_key:
            st.error("⚠️ يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
        elif not user_query.strip():
            st.warning("⚠️ اكتب سؤالك أولاً.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                with st.spinner("جاري إعداد التوصية الهندسية..."):
                    response = model.generate_content(user_query)
                    st.markdown("---")
                    st.markdown("### 💡 الإجابة الهندسية:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")
