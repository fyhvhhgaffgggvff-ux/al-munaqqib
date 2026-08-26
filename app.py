import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------
# إعدادات الصفحة والواجهة
# -------------------------------------------------------------
st.set_page_config(
    page_title="تطبيق المنقب - تصميم الرفع الصناعي",
    page_icon="⚓",
    layout="wide"
)

st.title("⚓ وحدة تصميم أجهزة الرفع الصناعي (Artificial Lift Sizing)")
st.caption("برنامج المُنقّب الهندي - حساب وتحديد مقاسات مضخات المكبس (SRP) والمضخات الغاطسة (ESP) مع التجسيم البياني")

# -------------------------------------------------------------
# الشريط الجانبي (Sidebar)
# -------------------------------------------------------------
st.sidebar.header("🕹️ لوحة التحكم")
pump_type = st.sidebar.radio(
    "اختر نظام الرفع الصناعي المراد تصميمه:",
    ["مضخات المكبس (Sucker Rod Pump - SRP)", "المضخات الغاطسة الكهربائية (ESP)"]
)

# -------------------------------------------------------------
# 1. تصميم مضخات المكبس (SRP)
# -------------------------------------------------------------
if "Sucker Rod Pump" in pump_type:
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

        # تجهيز التقرير للتنزيل
        report_df = pd.DataFrame([{
            "العمق (ft)": depth,
            "معدل الإنتاج (BPD)": target_prod,
            "قطر المكبس (in)": round(plunger_dia, 2),
            "أقصى حمل (lbs)": round(peak_rod_load, 0),
            "قدرة المحرك (HP)": round(motor_hp, 1)
        }])
        
        csv_data = report_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل تقرير التصميم (CSV)",
            data=csv_data,
            file_name=f"SRP_Design_Report_{depth}ft.csv",
            mime="text/csv"
        )

    # رسم بياني تفاعلي
    st.markdown("---")
    st.subheader("📈 تحليلات تفاعلية: تغير القدرة الحصانية مع عمق البئر")
    depths = np.linspace(1000, 12000, 50)
    hps = [(target_prod * d * fluid_sg) / (135700 * 0.55) for d in depths]
    
    fig = px.line(
        x=depths, y=hps,
        labels={"x": "عمق البئر (ft)", "y": "القدرة الحصانية المطلوبة (HP)"},
        title="تأثير العمق على استهلاك القدرة للمحرك"
    )
    fig.add_scatter(x=[depth], y=[motor_hp], mode='markers', marker=dict(size=12, color='red'), name='البئر الحالي')
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# 2. تصميم المضخات الغاطسة الكهربائية (ESP)
# -------------------------------------------------------------
else:
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

    # حسابات ESP
    head_from_depth = esp_depth
    head_from_pressures = ((thp - pip) * 2.31) / esp_sg
    tdh = head_from_depth + head_from_pressures
    avg_head_per_stage = 25.0
    stages = int(np.ceil(tdh / avg_head_per_stage))
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

        # تجهيز التقرير للتنزيل
        report_esp = pd.DataFrame([{
            "عمق المضخة (ft)": esp_depth,
            "التدفق (BPD)": esp_q,
            "الرأس الديناميكي TDH (ft)": round(tdh, 0),
            "عدد المراحل": stages,
            "قدرة المحرك (HP)": round(esp_hp, 1)
        }])
        
        csv_esp = report_esp.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل تقرير ESP (CSV)",
            data=csv_esp,
            file_name=f"ESP_Design_Report_{esp_depth}ft.csv",
            mime="text/csv"
        )

    # رسم منحنى الأداء الإفتراضي للمضخة (Pump Head vs Capacity)
    st.markdown("---")
    st.subheader("📈 منحنى أداء المضخة ونقطة التشغيل (H-Q Curve)")
    
    q_range = np.linspace(100, esp_q * 1.6, 50)
    # منحنى أداء فرضي للمضخة (حيث يقل الـ Head مع زيادة التدفق Q)
    head_curve = tdh * 1.3 - (0.3 * tdh * (q_range / esp_q)**2)
    
    fig_esp = go.Figure()
    fig_esp.add_trace(go.Scatter(x=q_range, y=head_curve, mode='lines', name='منحنى أداء المضخة (Head Curve)'))
    fig_esp.add_trace(go.Scatter(x=[esp_q], y=[tdh], mode='markers', marker=dict(size=14, color='green'), name='نقطة التشغيل المستهدفة'))
    fig_esp.update_layout(
        title="منحنى الأداء التقديري لمضخة ESP",
        xaxis_title="معدل التدفق (BPD)",
        yaxis_title="إجمالي الرفع - Head (ft)"
    )
    st.plotly_chart(fig_esp, use_container_width=True)
