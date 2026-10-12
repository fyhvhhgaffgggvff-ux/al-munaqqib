from __future__ import annotations

import io
import math
from datetime import datetime, timezone
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

try:
    import lasio
except ImportError:  # Friendly runtime message if dependency is missing
    lasio = None

try:
    from google import genai
except ImportError:
    genai = None

st.set_page_config(page_title="Al-Munaqqib | المُنقّب", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

TRANSLATIONS = {
    "العربية": {
        "title": "⚡ منصة المُنقّب الهندسية المتكاملة",
        "subtitle": "أدوات أولية لهندسة الإنتاج وتحليل بيانات الآبار — تحقّق من النتائج قبل استخدامها ميدانياً.",
        "tabs": ["🎯 الترشيح والاقتصاديات", "⚙️ تصميم SRP", "⚡ تصميم ESP", "📈 منحنى IPR", "📁 تحليل الملفات", "🤖 المساعد الذكي", "📄 التقارير"],
        "target": "الإنتاج المستهدف (BPD)", "depth": "العمق (ft)", "gor": "نسبة الغاز إلى النفط (scf/stb)", "visc": "اللزوجة (cP)",
        "screen": "ترشيح نظام الرفع", "srp": "تصميم مضخة القضيب (SRP)", "esp": "تصميم المضخة الكهربائية الغاطسة (ESP)",
        "ipr": "منحنى أداء التدفق (Vogel IPR)", "files": "تحليل سجلات الآبار والبيانات", "ai": "المساعد الهندسي بالذكاء الاصطناعي", "reports": "التقارير الشاملة",
    },
    "English": {
        "title": "⚡ Al-Munaqqib Engineering Suite",
        "subtitle": "Preliminary production-engineering tools and well-data analysis. Verify results before field use.",
        "tabs": ["🎯 Screening & Economics", "⚙️ SRP Design", "⚡ ESP Design", "📈 IPR Curve", "📁 File Analysis", "🤖 AI Assistant", "📄 Reports"],
        "target": "Target production (BPD)", "depth": "Depth (ft)", "gor": "Gas-oil ratio (scf/stb)", "visc": "Viscosity (cP)",
        "screen": "Artificial-lift screening", "srp": "Sucker Rod Pump (SRP)", "esp": "Electric Submersible Pump (ESP)",
        "ipr": "Inflow Performance Relationship (Vogel IPR)", "files": "Well-log and data analysis", "ai": "AI engineering assistant", "reports": "Comprehensive reports",
    },
}

from core import screen_lift_system, calculate_srp, calculate_esp, vogel_ipr, read_uploaded_data, summarize_dataframe, make_report

# ---------- UI ----------
with st.sidebar:
    st.header("⚙️ Settings / الإعدادات")
    lang = st.selectbox("🌐 اللغة / Language", ["العربية", "English"])
    api_key = st.text_input("Gemini API key (optional)", type="password", help="لا تضع المفتاح داخل الكود أو GitHub. يُستخدم فقط عند طلب المساعد.")
    st.caption("Al-Munaqqib v6 — preliminary engineering tool")
t = TRANSLATIONS[lang]

st.title(t["title"])
st.caption(t["subtitle"])
st.warning("تنبيه هندسي: النتائج تقديرية وليست بديلاً عن تصميم معتمد أو مراجعة مهندس مختص. راجع الوحدات والافتراضات قبل أي استخدام ميداني." if lang == "العربية" else "Engineering notice: results are estimates, not an approved design. Verify units and assumptions before field use.")
tabs = st.tabs(t["tabs"])
report: dict[str, str] = {}

with tabs[0]:
    st.subheader(t["screen"])
    c1, c2 = st.columns(2)
    with c1:
        q_target = st.number_input(t["target"], min_value=1.0, value=2500.0, step=100.0)
        depth = st.number_input(t["depth"], min_value=1.0, value=7000.0, step=250.0)
    with c2:
        gor = st.number_input(t["gor"], min_value=0.0, value=500.0, step=50.0)
        viscosity = st.number_input(t["visc"], min_value=0.1, value=15.0, step=1.0)
    if st.button("ترشيح النظام وحساب التقدير" if lang == "العربية" else "Screen system and estimate costs", type="primary", use_container_width=True):
        try:
            result = screen_lift_system(q_target, depth, gor, viscosity)
            st.success(f"التوصية المبدئية: {result['system']}" if lang == "العربية" else f"Preliminary recommendation: {result['system']}")
            a, b = st.columns(2)
            a.metric("CAPEX estimate", f"${result['capex_usd_estimate']:,.0f}")
            b.metric("OPEX estimate/day", f"${result['opex_usd_day_estimate']:,.0f}")
            st.info(result["note"])
            report["Screening"] = f"Production={q_target} BPD; depth={depth} ft; GOR={gor}; viscosity={viscosity} cP; recommendation={result['system']}; CAPEX estimate=${result['capex_usd_estimate']}; OPEX estimate=${result['opex_usd_day_estimate']}/day. {result['note']}"
        except ValueError as e:
            st.error(str(e))

with tabs[1]:
    st.subheader(t["srp"])
    a, b = st.columns(2)
    with a:
        srp_depth = st.number_input("Pump depth (ft)", min_value=1.0, value=5000.0, key="srp_depth")
        srp_q = st.number_input("Production (BPD)", min_value=1.0, value=300.0, key="srp_q")
    with b:
        stroke = st.number_input("Stroke length (in)", min_value=1.0, value=86.0, key="srp_stroke")
        spm = st.number_input("Strokes per minute (SPM)", min_value=0.1, value=12.0, key="srp_spm")
        eff = st.slider("Volumetric efficiency assumption", min_value=0.1, max_value=1.0, value=0.8, step=0.05)
    try:
        result = calculate_srp(srp_depth, srp_q, stroke, spm, eff)
        m1, m2, m3 = st.columns(3)
        m1.metric("Plunger diameter (in, estimate)", f"{result['plunger_diameter_in_estimate']:.2f}")
        m2.metric("Peak load (lbf, rough estimate)", f"{result['peak_load_lbf_estimate']:,.0f}")
        m3.metric("Motor HP (rough estimate)", f"{result['motor_hp_estimate']:.1f}")
        st.caption("Simplified estimate only. It does not replace API RP 11L, rod-string design, fluid level, dynamometer cards, friction or manufacturer selection.")
        report["SRP"] = str(result) + f" Inputs: depth={srp_depth} ft, rate={srp_q} BPD, stroke={stroke} in, SPM={spm}, efficiency={eff}. Simplified estimate only."
    except ValueError as e:
        st.error(str(e))

with tabs[2]:
    st.subheader(t["esp"])
    a, b = st.columns(2)
    with a:
        esp_depth = st.number_input("Pump depth (ft)", min_value=1.0, value=7500.0, key="esp_depth")
        esp_q = st.number_input("Production (BPD)", min_value=1.0, value=4000.0, key="esp_q")
    with b:
        head_stage = st.number_input("Head per stage (ft)", min_value=0.1, value=25.0, key="esp_head")
        surface_pressure = st.number_input("Surface pressure (psi)", min_value=0.0, value=200.0, key="esp_pressure")
    try:
        result = calculate_esp(esp_depth, esp_q, head_stage, surface_pressure)
        m1, m2, m3 = st.columns(3)
        m1.metric("TDH estimate (ft)", f"{result['tdh_ft_estimate']:,.0f}")
        m2.metric("Stages estimate", f"{int(result['stages_estimate'])}")
        m3.metric("HP placeholder", f"{result['motor_hp_placeholder_estimate']:.1f}")
        st.caption("TDH and stage count are simplified. The HP figure is only a placeholder and must not be used for motor selection without fluid specific gravity, efficiency, friction losses, intake pressure and pump curves.")
        report["ESP"] = str(result) + f" Inputs: depth={esp_depth} ft, rate={esp_q} BPD, head/stage={head_stage} ft, surface pressure={surface_pressure} psi. Validate with fluid gradient, friction and vendor curves."
    except ValueError as e:
        st.error(str(e))

with tabs[3]:
    st.subheader(t["ipr"])
    a, b = st.columns(2)
    with a:
        p_res = st.number_input("Reservoir pressure Pres (psi)", min_value=1.0, value=3000.0)
        q_test = st.number_input("Test flow rate (BPD)", min_value=0.1, value=1000.0)
    with b:
        p_wf = st.number_input("Test flowing pressure Pwf (psi)", min_value=0.0, value=2000.0)
    try:
        qmax, q_arr, pwf_arr = vogel_ipr(p_res, q_test, p_wf)
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(q_arr, pwf_arr, linewidth=2, label="Vogel IPR")
        ax.scatter([q_test], [p_wf], color="red", zorder=3, label=f"Test point ({q_test:g} BPD)")
        ax.set_xlabel("Flow rate Q (BPD)")
        ax.set_ylabel("Bottomhole flowing pressure Pwf (psi)")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.metric("AOF estimate (BPD)", f"{qmax:,.1f}")
        st.caption("Vogel correlation is an approximation for suitable solution-gas-drive reservoirs; verify applicability and test data quality.")
        report["IPR"] = f"Pres={p_res} psi; test rate={q_test} BPD; test Pwf={p_wf} psi; AOF estimate={qmax:.2f} BPD. Vogel applicability must be checked."
    except ValueError as e:
        st.error(str(e))

with tabs[4]:
    st.subheader(t["files"])
    uploaded = st.file_uploader("Upload LAS, CSV, XLSX or XLS", type=["las", "csv", "xlsx", "xls"])
    if uploaded:
        try:
            df, meta = read_uploaded_data(uploaded.name, uploaded.getvalue())
            st.success(f"Loaded {meta['format']} · {meta['rows']:,} rows × {meta['columns']} columns")
            x1, x2, x3 = st.columns(3)
            x1.metric("Rows", f"{meta['rows']:,}")
            x2.metric("Columns", meta["columns"])
            x3.metric("Missing cells", f"{meta['missing_cells']:,}")
            if meta.get("well_name"):
                st.write(f"**Well:** {meta['well_name']}")
            st.write("**Data preview**")
            st.dataframe(df.head(100), use_container_width=True)
            summary = summarize_dataframe(df)
            st.write("**Curve / column statistics**")
            st.dataframe(summary, use_container_width=True)
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and df[c].notna().any()]
            if len(numeric_cols) >= 1:
                default_x = meta.get("depth_curve") if meta.get("depth_curve") in numeric_cols else numeric_cols[0]
                x_col = st.selectbox("X axis (depth or index)", numeric_cols, index=numeric_cols.index(default_x))
                y_candidates = [c for c in numeric_cols if c != x_col]
                if y_candidates:
                    y_cols = st.multiselect("Curves to plot", y_candidates, default=y_candidates[:min(3, len(y_candidates))])
                    if y_cols:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        plot_df = df[[x_col] + y_cols].dropna(subset=[x_col]).sort_values(x_col)
                        for col in y_cols:
                            ax.plot(plot_df[col], plot_df[x_col], label=str(col), linewidth=1)
                        ax.set_xlabel("Curve value")
                        ax.set_ylabel(str(x_col))
                        ax.invert_yaxis() if "depth" in x_col.lower() or x_col.lower() in {"dept", "depth", "md", "tvd"} else None
                        ax.grid(True, alpha=0.3)
                        ax.legend(loc="best")
                        fig.tight_layout()
                        st.pyplot(fig)
                        plt.close(fig)
            csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("Download normalized data as CSV", csv_bytes, file_name="munaqqib_normalized_data.csv", mime="text/csv")
            st.download_button("Download column statistics as CSV", summary.to_csv(index=False).encode("utf-8-sig"), file_name="munaqqib_curve_statistics.csv", mime="text/csv")
            report["File analysis"] = f"File={uploaded.name}; format={meta['format']}; rows={meta['rows']}; columns={meta['columns']}; missing cells={meta['missing_cells']}; columns={', '.join(map(str, df.columns))}."
        except Exception as e:
            st.error(f"Could not analyze this file: {e}")
            st.caption("Check that the file is not corrupt, the extension matches its format, and required packages are installed.")

with tabs[5]:
    st.subheader(t["ai"])
    prompt = st.text_area("اكتب سؤالك الهندسي / Enter your engineering question", height=140)
    if st.button("تحليل السؤال بواسطة Gemini / Ask Gemini", use_container_width=True):
        if not api_key.strip():
            st.error("أدخل Gemini API key في الإعدادات أولاً. / Add your Gemini API key in Settings first.")
        elif not prompt.strip():
            st.error("اكتب السؤال أولاً. / Enter a question first.")
        elif genai is None:
            st.error("Google GenAI SDK is not installed. Run pip install -r requirements.txt.")
        else:
            try:
                with st.spinner("جارٍ التحليل... / Analyzing..."):
                    client = genai.Client(api_key=api_key.strip())
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents="You are a cautious petroleum engineering assistant. State assumptions, units, uncertainty, and when field/vendor verification is needed. Do not invent measured data. Question: " + prompt.strip(),
                    )
                answer = response.text or "No text response returned."
                st.markdown("### التوصية / Recommendation")
                st.write(answer)
                report["AI consultation"] = f"Question: {prompt}\nAnswer: {answer}"
            except Exception as e:
                st.error(f"Gemini request failed: {e}")

with tabs[6]:
    st.subheader(t["reports"])
    st.write("يضم التقرير النتائج التي تم إنشاؤها في التبويبات الحالية خلال جلسة التطبيق. شغّل الحساب أو التحليل المطلوب أولاً، ثم نزّل التقرير." if lang == "العربية" else "The report includes results generated in the current app session. Run the relevant calculation or analysis first, then download.")
    if report:
        st.json(report)
    else:
        st.info("لا توجد نتائج محفوظة في هذه الجلسة بعد." if lang == "العربية" else "No results recorded in this session yet.")
    content = make_report(report)
    st.download_button("📥 تنزيل التقرير الشامل TXT", content.encode("utf-8-sig"), file_name="Al_Munaqqib_Preliminary_Report.txt", mime="text/plain;charset=utf-8", use_container_width=True)

st.divider()
st.caption("Al-Munaqqib v6 · Preliminary educational/engineering support only · Keep API keys private.")
