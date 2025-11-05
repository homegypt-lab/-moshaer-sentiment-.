import streamlit as st
from transformers import pipeline
import csv
import os
from datetime import datetime
import requests

st.set_page_config(page_title="مشاعر | تحليل تعليقات بالعربي", page_icon="💬", layout="centered")

st.markdown(
    """
    <div style="text-align:center;">
        <h1>💬 مشاعر</h1>
        <h3>تحليل مشاعر التعليقات بالعربية (إيجابي / سلبي / محايد) + درجة الثقة</h3>
        <p>تابع عملاءك بذكاء: نجمع البيانات تلقائيًا (الرقم، التعليق، النتيجة، الموقع، وسيلة الدفع)</p>
        <hr/>
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def load_analyzer():
    return pipeline("sentiment-analysis", model="aubmindlab/bert-base-arabertv2")

analyzer = load_analyzer()

if "trial_count" not in st.session_state:
    st.session_state.trial_count = 0

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_score" not in st.session_state:
    st.session_state.last_score = None

st.subheader("اكتب تعليقك للتحليل")
user_input = st.text_area("اكتب تعليقك هنا:", placeholder="مثال: الخدمة ممتازة وسريعة جدًا!")

col_analyze, col_trials = st.columns([1, 1])
with col_analyze:
    analyze_clicked = st.button("تحليل التعليق الآن")
with col_trials:
    st.info(f"المحاولات المجانية المتبقية: {max(0, 2 - st.session_state.trial_count)}")

if analyze_clicked:
    if st.session_state.trial_count < 2:
        if user_input.strip() != "":
            result = analyzer(user_input)
            label = result[0]["label"]
            score = result[0]["score"]
            st.success(f"النتيجة: {label}  |  درجة الثقة: {score:.2f}")
            st.session_state.trial_count += 1
            st.session_state.last_result = label
            st.session_state.last_score = score
        else:
            st.warning("من فضلك اكتب تعليقًا أولًا.")
    else:
        st.error("انتهت محاولاتك المجانية. يمكنك الاشتراك أو ترك رقمك للتواصل عبر واتساب.")

st.markdown("---")
st.subheader("الاشتراك وطريقة الدفع")

option = st.radio(
    "اختر وسيلة الدفع المناسبة:",
    ("تحويل بنكي", "البريد المصري", "فودافون كاش", "PayPal", "وسيلة أخرى"),
    index=2
)

if option == "تحويل بنكي":
    st.info("برجاء التحويل على الحساب البنكي: XXXX-XXXX-XXXX")
elif option == "البريد المصري":
    st.info("برجاء الدفع عبر خدمة البريد المصري على رقم الحساب: XXXX")
elif option == "فودافون كاش":
    st.info("برجاء التحويل على رقم: 01225957590")
elif option == "PayPal":
    st.markdown("[اضغط للدفع عبر PayPal](https://www.paypal.com/)", unsafe_allow_html=True)
else:
    st.info("تواصل معنا لتحديد وسيلة دفع أخرى تناسبك.")

st.markdown("---")
st.subheader("التواصل عبر واتساب")
st.markdown("اكتب رقمك وسنقوم بالتواصل معك عبر واتساب لتفعيل الاشتراك أو الرد على استفسارك.")

phone_number = st.text_input("رقمك للتواصل عبر واتساب:", placeholder="مثال: 01225957590")

company_whatsapp = "01225957590"
wa_link = f"https://wa.me/2{company_whatsapp}"
st.markdown(f"[تواصل مباشر مع مشاعر على واتساب]({wa_link})", unsafe_allow_html=True)

save_clicked = st.button("إرسال رقم للتواصل")

def get_geo():
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        data = resp.json()
        return data.get("ip", "غير متاح"), data.get("city", "غير متاح"), data.get("country", "غير متاح")
    except Exception:
        return "غير متاح", "غير متاح", "غير متاح"

def save_client_row(row):
    file_exists = os.path.isfile("clients.csv")
    with open("clients.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "رقم العميل","تاريخ ووقت الإدخال","وسيلة الدفع","التعليق",
                "نتيجة التحليل","درجة الثقة","IP","المدينة","الدولة"
            ])
        writer.writerow(row)

if save_clicked:
    if phone_number.strip() == "":
        st.warning("من فضلك اكتب رقمك أولًا.")
    else:
        ip, city, country = get_geo()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sentiment = st.session_state.last_result if st.session_state.last_result else "غير متاح"
        score_str = f"{st.session_state.last_score:.2f}" if st.session_state.last_score else "غير متاح"

        save_client_row([
            phone_number,timestamp,option,user_input,sentiment,score_str,ip,city,country
        ])

        st.success(f"تم استلام رقمك: {phone_number}. سنتواصل معك قريبًا عبر واتساب.")
        st.info("تم حفظ بياناتك في clients.csv (يمكن تنزيل الملف من القائمة الجانبية).")

st.markdown("---")
st.subheader("تنزيل قاعدة بيانات العملاء")
if os.path.isfile("clients.csv"):
    with open("clients.csv", "rb") as f:
        st.download_button(
            label="تنزيل ملف العملاء (CSV)",
            data=f,
            file_name="clients.csv",
            mime="text/csv"
        )
else:
    st.caption("لم يتم إنشاء الملف بعد. سيتم إنشاؤه عند أول عميل يرسل رقمه.")

st.markdown(
    """
    <hr/>
    <div style="text-align:center; font-size: 14px;">
        © مشاعر — خدمة تحليل مشاعر التعليقات بالعربية. للتواصل: 01225957590
    </div>
    """,
    unsafe_allow_html=True
)
