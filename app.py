import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

st.set_page_config(page_title="UMKM AI Analyst", layout="wide")

client = Groq(api_key=st.secrets["GROQ_KEY"])

# =========================
# SIDEBAR
# =========================

st.sidebar.title("UMKM AI Analyst")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Marketplace Analysis",
        "Forecast",
        "Pricing Lab",
        "AI Consultant"
    ]
)

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# =========================
# DATA PROCESSING
# =========================

def preprocess(df):

    df.columns = df.columns.str.lower().str.strip()

    if {"price", "quantity"}.issubset(df.columns):
        df["revenue"] = df["price"] * df["quantity"]

    if {"price", "cost", "quantity"}.issubset(df.columns):
        df["profit"] = (df["price"] - df["cost"]) * df["quantity"]

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.to_period("W").astype(str)
        df["month"] = df["date"].dt.to_period("M").astype(str)

    return df


if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df = preprocess(df)

# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":

    st.title("📊 Business Dashboard")

    if not uploaded_file:
        st.info("Upload data CSV di sidebar untuk memulai.")
    else:

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Revenue", f"Rp {df['revenue'].sum():,.0f}")
        col2.metric("Total Profit", f"Rp {df['profit'].sum():,.0f}")
        col3.metric("Total Orders", df.shape[0])

        st.divider()

        if {"product_name", "quantity"}.issubset(df.columns):

            st.subheader("Top Selling Products")

            top_products = (
                df.groupby("product_name")["quantity"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.bar_chart(top_products)

        if {"month", "quantity"}.issubset(df.columns):

            st.subheader("Monthly Sales")

            monthly = df.groupby("month")["quantity"].sum()

            st.line_chart(monthly)

# =========================
# MARKETPLACE ANALYSIS
# =========================

elif menu == "Marketplace Analysis":

    st.title("🛒 Marketplace Comparison")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:

        if {"marketplace", "revenue"}.issubset(df.columns):

            marketplace_sales = df.groupby("marketplace")["revenue"].sum()

            st.bar_chart(marketplace_sales)

            st.write("Revenue per Marketplace")

            st.dataframe(marketplace_sales)

# =========================
# FORECAST
# =========================

elif menu == "Forecast":

    st.title("📈 Sales Forecast")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:

        if {"month", "quantity"}.issubset(df.columns):

            monthly = df.groupby("month")["quantity"].sum()

            forecast = monthly.mean()

            st.line_chart(monthly)

            st.metric(
                "Prediksi Penjualan Bulan Depan",
                f"{forecast:.0f} unit"
            )

# =========================
# PRICING LAB
# =========================

elif menu == "Pricing Lab":

    st.title("🧪 Pricing Simulation")

    if not uploaded_file:
        st.info("Upload data terlebih dahulu.")
    else:

        if {"product_name", "cost"}.issubset(df.columns):

            markup = st.slider("Markup (%)", 0, 200, 50)

            df["simulated_price"] = df["cost"] * (1 + markup / 100)

            st.write("Simulasi harga baru")

            st.dataframe(
                df[["product_name", "cost", "simulated_price"]].head(20)
            )

# =========================
# AI CONSULTANT
# =========================

elif menu == "AI Consultant":

    st.title("🤖 AI Business Consultant")

    question = st.text_area("Tanyakan sesuatu tentang bisnis Anda")

    if st.button("Tanya AI"):

        with st.spinner("AI sedang berpikir..."):

            response = client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                model="llama-3.1-8b-instant",
            )

            st.write(response.choices[0].message.content)

    if uploaded_file:

        st.divider()

        if st.button("Generate AI Business Insight"):

            summary = df.describe(include="all").to_string()

            prompt = f"""
            Berikut data bisnis fashion/retail:

            {summary}

            Berikan:
            - insight utama
            - produk paling potensial
            - risiko bisnis
            - strategi yang direkomendasikan
            """

            with st.spinner("AI menganalisis data..."):

                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                )

                st.write(response.choices[0].message.content)




