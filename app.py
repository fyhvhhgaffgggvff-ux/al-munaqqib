import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="منصة المنقب الهندسي", page_icon="🛢️", layout="wide")

if "db_users" not in st.session_state:
    st.session_state["db_users"] = {
        "mohammed": {"pass": "123", "name": "المهندس محمد", "status": "نشط"}
    }

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 منصة المنقب الهندسي")
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
    
    with tab1:
        u_login = st.text_input("اسم المستخدم أو البريد")
        p_login = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            users = st.session_state["db_users"]
            if u_login in users and users[u_login]["pass"] == p_login:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = u_login
                st.session_state["user_name"] = users[u_login]["name"]
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    with tab2:
        st.subheader("اشتراك جديد في المنصة")
        new_name = st.text_input("الاسم الكامل (المهندس/الشركة)")
        new_user = st.text_input("اسم المستخدم الجديد")
        new_pass = st.text_input("أنشئ كلمة المرور", type="password")
        plan = st.selectbox("اختر خطة الاشتراك", ["الخطة الشهرية ($15)", "الخطة السنوية ($120)"])
        
        if st.button("إتمام التسجيل والتحويل للدفع"):
            if new_user and new_pass and new_name:
                st.session_state["db_users"][new_user] = {
                    "pass": new_pass,
                    "name": new_name,
                    "status": "معلق (في انتظار الدفع)"
                }
                st.success("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول والانتقال لتأكيد الدفع.")
            else:
                st.warning("يرجى تعبئة كافة الحقول المطلوبة")

else:
    st.sidebar.title(f"مرحباً م. {st.session_state['user_name']}")
    page = st.sidebar.radio("الخدمات:", ["حاسبة OOIP", "تقارير الحسابات", "بوابة السداد والدفع"])
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.rerun()

    if page == "حاسبة OOIP":
        st.title("🛢️ حاسبة حجم النفط الأصلي (OOIP)")
        c1, c2 = st.columns(2)
        with c1:
            A = st.number_input("المساحة A (Acres):", value=500.0)
            h = st.number_input("السمك h (Feet):", value=30.0)
            Bo = st.number_input("معامل Bo:", value=1.25)
        with c2:
            phi = st.number_input("المسامية Porosity:", value=0.20)
            Sw = st.number_input("تشبع الماء Sw:", value=0.25)

        ooip = (7758 * A * h * phi * (1 - Sw)) / Bo
        st.markdown("---")
        st.metric("الاحتياطي المحسوب (STB):", f"{ooip:,.2f}")
            # رسم منحنى الحساسية
    porosity_range = np.linspace(0.05, 0.35, 50)
    stb_values = [(7758 * A * h * p * (1 - Sw)) / Bo for p in porosity_range]
    
        porosity_range = np.linspace(0.05, 0.35, 50)
    stb_values = [(7758 * A * h * p * (1 - Sw)) / Bo for p in porosity_range]

    fig, ax = plt.subplots()
    ax.plot(porosity_range * 100, stb_values, color="green", linewidth=2)
    ax.set_xlabel("Porosity (%)")
    ax.set_ylabel("OOIP (STB)")
    ax.set_title("Effect of Porosity on OOIP")
    ax.grid(True)

    st.pyplot(fig)

elif page == "تقارير الحسابات":


    elif page == "تقارير الحسابات":
        st.title("📄 تصدير البيانات والتقارير")
        df = pd.DataFrame([{"المهندس": st.session_state['user_name'], "النتيجة OOIP (STB)": "حُسبت بنجاح"}])
        st.dataframe(df)

    elif page == "بوابة السداد والدفع":
        st.title("💳 وسائل الدفع وتفعيل الاشتراك")
        st.write("اختر طريقة السداد المناسبة لربط حسابك وتفعيله:")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("1. الدفع بالبطاقات البنكية (Stripe)")
            st.button("💳 دفع 15$ بالبطاقة")
        with c2:
            st.subheader("2. الدفع بالعملات الرقمية (USDT)")
            st.code("TRX-Wallet: TXXXXXX...XXXXX", language="text")
            st.button("✅ تأكيد التحويل الرقمي")
            # إضافة رسم بياني لتحليل الحساسية
st.write("---")
st.subheader("📊 تحليل حساسيات المكمن (Sensitivities)")

porosity_range = np.linspace(0.05, 0.35, 50)
stb_values = [(7758 * 500 * 30 * p * (1 - 0.25)) / 1.25 for p in porosity_range]

fig, ax = plt.subplots()
ax.plot(porosity_range * 100, stb_values, color="green", linewidth=2)
ax.set_xlabel("Porosity (%)")
ax.set_ylabel("STOIIP (STB)")
ax.set_title("Effect of Porosity on STOIIP")
ax.grid(True)

st.pyplot(fig)

