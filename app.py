import streamlit as st
import numpy as np
import pandas as pd
import google.generativeai as genai

# ---------------------------------------------------------
# إعدادات الصفحة والواجهة
# ---------------------------------------------------------
st.set_page_config(
    page_title="تصميم الرفع الصناعي والذكاء الاصطناعي",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ برنامج المُنقّب - المدعوم بالذكاء الاصطناعي")
st.caption("مساعد هندسة النفط الذكية: تصميم أجهزة الرفع الصناعي واستشارات Gemini الذكية")

# ---------------------------------------------------------
# الشريط الجانبي (Sidebar)
# ---------------------------------------------------------
st.sidebar.header("🔑 إعدادات الذكاء الاصطناعي")
api_key = st.sidebar.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")

st.sidebar.header("⚙️ مدخلات بيانات البئر")
flow_rate = st.sidebar.number_input("معدل الإنتاج المطلوب (BPD)", min_value=100, max_value=10000, value=1500, step=100)
depth = st.sidebar.number_input("عمق البئر (ft)", min_value=1000, max_value=20000, value=6000, step=500)
gor = st.sidebar.number_input("نسبة الغاز للنفط GOR (scf/STB)", min_value=0, max_value=5000, value=300, step=50)
bsw = st.sidebar.slider("نسبة القطع المائي BS&W (%)", 0, 100, 20)
viscosity = st.sidebar.number_input("اللزوجة (cP)", min_value=0.5, max_value=500.0, value=5.0, step=0.5)

# ---------------------------------------------------------
# منطق ترشيح نظام الرفع الصناعي (Rule-Based)
# ---------------------------------------------------------
def recommend_lift_system(rate, d, g, water_cut, visc):
    reasons = []
    
    if rate > 3000 and g < 1000 and visc < 20:
        system = "ESP (المضخة الكهربائية الغاطسة)"
        reasons.append("معدل إنتاج عالٍ جداً ولزوجة منخفضة يناسبها نظام ESP.")
    elif rate < 1000 and d < 9000 and g < 500:
        system = "SRP (مضخة القضبان الشفاطة)"
        reasons.append("معدل إنتاج متوسط/منخفض وعمق مناسب لنظام SRP.")
    elif g > 800:
        system = "Gas Lift (الرفع بالغاز)"
        reasons.append("نسبة غاز عالية (GOR) تجعل الرفع بالغاز الخيار الأمثل والأنشط.")
    elif visc > 50:
        system = "PCP (المضخة اللولبية التقدمية)"
        reasons.append("اللزوجة العالية للمائع تمنح الأفضلية لنظام PCP.")
    else:
        system = "ESP (المضخة الكهربائية الغاطسة)"
        reasons.append("تم اختيار ESP بناءً على متطلبات الإنتاج العامة.")
        
    return system, reasons

recommended_system, system_reasons = recommend_lift_system(flow_rate, depth, gor, bsw, viscosity)

# ---------------------------------------------------------
# عرض نتائج التوصية الأساسية
# ---------------------------------------------------------
st.subheader("🎯 التوصية الأولية لنظام الرفع المناسب")
col1, col2 = st.columns(2)

with col1:
    st.success(f"النظام المقترح: **{recommended_system}**")
    for r in system_reasons:
        st.write(f"- {r}")

with col2:
    st.info("📊 ملخص بيانات البئر المدخلة:")
    st.write(f"- العمق: {depth} ft")
    st.write(f"- معدل التدفق: {flow_rate} BPD")
    st.write(f"- نسبة القطع المائي: {bsw}%")
    st.write(f"- نسبة الغاز للنفط: {gor} scf/STB")

st.divider()

# ---------------------------------------------------------
# قسم المساعد الهندسي الذكي (Gemini AI)
# ---------------------------------------------------------
st.subheader("🤖 المساعد الهندسي الذكي (Gemini AI)")

user_query = st.text_area(
    "اكتب استفسارك الهندسي هنا (مثال: متى أختار SRP بدلاً من ESP؟ أو ما أسباب انخفاض كفاءة المضخة؟):",
    height=100
)

if st.button("تحليل واستشارة الذكاء الاصطناعي 🧠"):
    if not api_key:
        st.error("⚠️ يرجى إدخل مفتاح Gemini API في الشريط الجانبي أولاً لتفعيل هذه الميزة!")
    elif not user_query.strip():
        st.warning("⚠️ يرجى كتابة سؤالك قبل الضغط على الزر.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            أنت خبير واستشاري في هندسة النفط ومتخصص في أجهزة الرفع الصناعي (Artificial Lift Systems).
            بناءً على بيانات البئر التالية:
            - العمق: {depth} ft
            - معدل التدفق: {flow_rate} BPD
            - GOR: {gor} scf/STB
            - BS&W: {bsw}%
            - اللزوجة: {viscosity} cP
            - النظام المقترح أولياً: {recommended_system}
            
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
