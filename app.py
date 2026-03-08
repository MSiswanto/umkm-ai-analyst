import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from groq import Groq
from dotenv import load_dotenv
import uuid

# =========================
# USER SESSION TRACKING
# =========================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# =========================
# EVENT TRACKING
# =========================

def log_event(event):

    data = {
        "timestamp": pd.Timestamp.now(),
        "user_id": st.session_state.user_id,
        "event": event
    }

    new = pd.DataFrame([data])

    try:
        old = pd.read_csv("events.csv")
        updated = pd.concat([old, new], ignore_index=True)
    except:
        updated = new

    updated.to_csv("events.csv", index=False)


load_dotenv(override=True)

st.set_page_config(page_title="UMKM AI Analyst", layout="wide")

client = Groq(api_key=st.secrets["GROQ_KEY"])

# =========================
# SIDEBAR
# =========================

st.sidebar.title("🚀 UMKM AI Analyst")

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Marketplace Intelligence",
        "Early Warning",
        "Forecast",
        "Pricing Lab",
        "AI Consultant",
        "Platform Analytics",
        "User Feedback"
    ]
)

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# =========================
# DATA PREPROCESSING
# =========================

def preprocess(df):

    df.columns = df.columns.str.lower().str.strip()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.to_period("W").astype(str)
        df["month"] = df["date"].dt.to_period("M").astype(str)

    if {"price","quantity"}.issubset(df.columns):
        df["revenue"] = df["price"] * df["quantity"]

    if {"price","cost","quantity"}.issubset(df.columns):
        df["profit"] = (df["price"] - df["cost"]) * df["quantity"]

    return df

# =========================
# LOAD DATA
# =========================

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = preprocess(df)
    log_event("dataset_uploaded")
    
# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":

    st.title("📊 Business Dashboard")

    if not uploaded_file:
        st.info("Upload data di sidebar untuk memulai.")
    else:

        col1,col2,col3 = st.columns(3)

        col1.metric("Total Revenue",f"Rp {df['revenue'].sum():,.0f}")
        col2.metric("Total Profit",f"Rp {df['profit'].sum():,.0f}")
        col3.metric("Transactions",df.shape[0])

        st.divider()

        if {"product_name","quantity"}.issubset(df.columns):

            st.subheader("Top Selling Products")

            top_products = (
                df.groupby("product_name")["quantity"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.bar_chart(top_products)

        if {"month","quantity"}.issubset(df.columns):
            st.subheader("Monthly Sales Trend")
            monthly = df.groupby("month")["quantity"].sum()
            st.line_chart(monthly)

# =========================
# MARKETPLACE INTELLIGENCE
# =========================

elif menu == "Marketplace Intelligence":

    st.title("🛒 Marketplace Intelligence")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:

        if {"marketplace","revenue"}.issubset(df.columns):
            revenue_market = df.groupby("marketplace")["revenue"].sum()
            st.subheader("Revenue by Marketplace")
            st.bar_chart(revenue_market)
            best = revenue_market.idxmax()
            st.success(f"Marketplace dengan performa terbaik: **{best}**")

# =========================
# EARLY WARNING
# =========================

elif menu == "Early Warning":

    st.title("⚠️ Business Risk Detection")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:

        if {"product_name","quantity"}.issubset(df.columns):

            product_sales = (
                df.groupby("product_name")["quantity"]
                .sum()
                .sort_values()
                .head(5)
            )

            st.warning("Produk dengan penjualan terendah")
            st.dataframe(product_sales)

        if "profit" in df.columns:
            low_margin = df[df["profit"] < 0]

            if len(low_margin) > 0:
                st.error("Ada transaksi dengan profit negatif")
                st.dataframe(low_margin.head())

# =========================
# FORECAST
# =========================

elif menu == "Forecast":

    st.title("📈 Demand Forecast")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:
        if {"month","quantity"}.issubset(df.columns):
            monthly = df.groupby("month")["quantity"].sum()
            forecast = int(monthly.mean())
            st.line_chart(monthly)
            st.metric(
                "Prediksi Demand Bulan Depan",
                f"{forecast} unit"
            )
            log_event("forecast_used")
        
# =========================
# PRICING LAB
# =========================

elif menu == "Pricing Lab":

    st.title("🧪 Pricing Strategy Lab")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:

        if {"product_name","cost"}.issubset(df.columns):
            markup = st.slider("Markup (%)",0,200,50)
            df["sim_price"] = df["cost"] * (1 + markup/100)

            st.write("Simulasi harga baru")
            st.dataframe(
                df[["product_name","cost","sim_price"]]
                .head(20)
            )

# =========================
# AI CONSULTANT
# =========================

elif menu == "AI Consultant":

    st.title("🤖 AI Business Consultant")
    question = st.text_area("Tanyakan tentang bisnis fashion/retail")

    if st.button("Ask AI"):
        with st.spinner("AI sedang berpikir..."):
            response = client.chat.completions.create(
                messages=[{"role":"user","content":question}],
                model="llama-3.1-8b-instant"
            )
            st.write(response.choices[0].message.content)
            log_event("ai_consultant_used")

    if uploaded_file:
        st.divider()

        if st.button("Generate AI Business Insight"):
            summary = df.describe(include="all").to_string()
            prompt = f"""
            Berikut ringkasan data bisnis retail:
            {summary}

            Berikan:
            - insight utama
            - peluang bisnis
            - risiko
            - strategi peningkatan profit
            """

            with st.spinner("AI sedang menganalisis..."):

                response = client.chat.completions.create(
                    messages=[{"role":"user","content":prompt}],
                    model="llama-3.1-8b-instant"
                )

                st.write(response.choices[0].message.content)

# =========================
# PLATFORM ANALYTICS
# =========================

elif menu == "Platform Analytics":
    st.title("📊 Platform Usage Analytics")
    try:
        events = pd.read_csv("events.csv")
        col1,col2 = st.columns(2)
        col1.metric("Total Events", len(events))
        col2.metric("Total Users", events["user_id"].nunique())
        st.subheader("Feature Usage")
        usage = events["event"].value_counts()
        st.bar_chart(usage)

    except:
        st.info("Belum ada data usage.")


# =========================
# USER FEEDBACK
# =========================

elif menu == "User Feedback":

    st.title("💬 Beri Feedback")
    st.write("Masukan Anda membantu kami meningkatkan platform ini.")

    name = st.text_input("Nama (opsional)")
    phone = st.text_input("Nomor HP / WhatsApp")

    rating = st.selectbox(
        "Rating Platform",
        ["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"]
    )

    rating_value = len(rating)

    feedback = st.text_area("Masukan / Saran")

    if st.button("Kirim Feedback"):

        if phone.strip() == "":
            st.error("Mohon isi nomor HP atau WhatsApp")

        else:

            new_data = pd.DataFrame([{
                "timestamp": pd.Timestamp.now(),
                "user_id": st.session_state.user_id,
                "name": name,
                "phone": phone,
                "rating": rating_value,
                "feedback": feedback
            }])
            
            st.download_button(
                "Download Feedback CSV",
                feedback_df.to_csv(index=False),
                "feedback.csv",
                "text/csv"
                )
            try:
                old_data = pd.read_csv("feedback.csv")
                updated = pd.concat([old_data, new_data], ignore_index=True)

            except:
                updated = new_data

            updated.to_csv("feedback.csv", index=False)

            st.success("Terima kasih atas feedback Anda!")

    st.divider()

    st.subheader("📊 Feedback dari Pengguna")

    try:

        feedback_df = pd.read_csv("feedback.csv")

        avg_rating = feedback_df["rating"].mean()

        col1, col2 = st.columns(2)

        col1.metric("Total Feedback", len(feedback_df))
        col2.metric("Average Rating", f"{avg_rating:.1f} ⭐")

        st.dataframe(feedback_df)

    except:
        st.info("Belum ada feedback.")
