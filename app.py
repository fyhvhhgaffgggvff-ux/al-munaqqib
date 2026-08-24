import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="منصة المنقب الهندسي", page_icon="🛢️", layout="wide")

# 1. قاعدة البيانات في الذاكرة
if "db_users" not in st.session_state:
    st.session_state["db_users"] = {
        "admin": {
            "pass": "1234", 
            "name": "المهندس محمد", 
            "join_date": datetime.now().date(),
            "is_paid": True
        }
    }

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# 2. شاشة تسجيل الدخول وإنشاء الحساب
if not st.session_state["authenticated"]:
    st.title("🔑 منصة المنقب الهندسي")
    
    tab1, tab2 = st.tabs(["إنشاء حساب جديد (تجربة مجانية 30 يوم)", "تسجيل الدخول"])
    
    with tab1:
        new_user = st.text_input("اختر اسم مستخدم (مثل: engineer1)")
        new_pass = st.text_input("اختر كلمة مرور", type="password")
        new_name = st.text_input("الاسم الكامل")
        
        if st.button("🚀 إنشاء حساب مجاني والدخول"):
            if new_user and new_pass:
                st.session_state["db_users"][new_user] = {
                    "pass": new_pass,
                    "name": new_name if new_name else new_user,
                    "join_date": datetime.now().date(),
                    "is_paid": False
                }
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = new_user
                st.success("تم إنشاء الحساب وتفعيله مجاناً لمدة 30 يوماً!")
                st.rerun()
            else:
                st.warning("يرجى ملء كافة الحقول (اسم المستخدم وكلمة المرور).")

    with tab2:
        username = st.text_input("اسم المستخدم", value="admin")
        password = st.text_input("كلمة المرور", type="password", value="1234")
        
        if st.button("تسجيل الدخول"):
            users = st.session_state["db_users"]
            if username in users and users[username]["pass"] == password:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = username
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

# 3. الشاشة الرئيسية بعد الدخول
else:
    user_id = st.session_state.get("user_id", "admin")
    user_data = st.session_state["db_users"].get(user_id, st.session_state["db_users"]["admin"])
    
    join_date = user_data["join_date"]
    days_used = (datetime.now().date() - join_date).days
    days_left = max(0, 30 - days_used)
    is_paid = user_data["is_paid"]

    st.sidebar.title(f"مرحباً {user_data['name']}")
    
    if is_paid:
        st.sidebar.success("👑 الحساب: مدفوع (مفعل بالكامل)")
    elif days_left > 0:
        st.sidebar.info(f"⏳ تجربة مجانية: متبقي {days_left} يوم")
    else:
        st.sidebar.error("⚠️ انتهت الفترة التجريبية!")

    page = st.sidebar.radio("القائمة الرئيسية", ["حاسبة OOIP", "تقارير الحسابات", "بوابة السداد والدفع"])
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state["authenticated"] = False
        st.rerun()

    has_access = is_paid or (days_left > 0)

    if page == "حاسبة OOIP":
        st.title("🛢️ حاسبة حجم النفط الأصلي (OOIP)")
        
        if not has_access:
            st.warning("🔒 انتهت فترتك التجريبية (30 يوماً). يرجى التوجه لصفحة بوابة السداد والدفع لتفعيل حسابك.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                A = st.number_input("المساحة A (Acres)", value=500.0)
                h = st.number_input("السمك h (Feet)", value=30.0)
                Bo = st.number_input("معامل Bo", value=1.25)
            with c2:
                phi = st.number_input("المسامية Porosity", value=0.20)
                Sw = st.number_input("تشبع الماء Sw", value=0.25)

            ooip = (7758 * A * h * phi * (1 - Sw)) / Bo
            st.markdown("---")
            st.metric("الاحتياطي المحسوب (STB):", f"{ooip:,.2f}")

            # رسم منحنى الحساسية
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
        st.title("📄 تصدير البيانات والتقارير")
        if not has_access:
            st.warning("🔒 الميزة متاحة للمشتركين فقط.")
        else:
            df = pd.DataFrame([{"المهندس": user_data["name"], "حالة الاشتراك": "نشط" if is_paid else "تجريبي"}])
            st.dataframe(df)

    elif page == "بوابة السداد والدفع":
        st.title("💳 وسائل الدفع وتفعيل الاشتراك")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("1. الدفع بالبطاقات البنكية")
            if st.button("دفع $15 بالبطاقة 💳"):
                user_data["is_paid"] = True
                st.success("تم تفعيل الحساب بنجاح!")
                st.rerun()
        with c2:
            st.subheader("2. الدفع بالعملات الرقمية")
            st.code("TRX-Wallet: TXXXXXX...")
            if st.button("تأكيد التحويل الرقمي ✅"):
                user_data["is_paid"] = True
                st.success("تم تفعيل الحساب بنجاح!")
                st.rerun()
