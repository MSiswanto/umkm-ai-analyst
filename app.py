import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

st.set_page_config(page_title="UMKM AI Analyst", layout="wide")

# ======================
# HEADER
# ======================

st.title("🚀 UMKM AI Analyst")
st.markdown(
"""
Platform analisis bisnis berbasis AI untuk membantu UMKM 
fashion & retail mengambil keputusan berbasis data secara cepat dan strategis.
"""
)

st.divider()

client = Groq(api_key=st.secrets["GROQ_KEY"])  # pakai Secrets Streamlit

# ======================
# CHAT SECTION
# ======================

st.header("💬 Konsultasi Bisnis dengan AI")

user_input = st.text_input("Tanyakan sesuatu tentang bisnis fashion/retail Anda")

if st.button("Kirim Pertanyaan"):
    if user_input:
        with st.spinner("AI sedang berpikir..."):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": user_input}],
                model="llama-3.1-8b-instant",
            )
            st.success(chat_completion.choices[0].message.content)

st.divider()

# ======================
# CSV ANALYSIS SECTION
# ======================

st.header("📊 Upload Data Penjualan (CSV)")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Preview Data")
    st.dataframe(df.head())

    # ======================
    # SIMPLE VISUALIZATION
    # ======================
    # Normalisasi kolom
    df.columns = df.columns.str.lower().str.strip()

    # Hitung total penjualan per produk
    if "product_name" in df.columns and "quantity" in df.columns:
        st.subheader("📈 Total Unit Terjual per Produk")

        sales_per_product = (
        df.groupby("product_name")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)   # tampilkan top 10 saja
        )

        st.bar_chart(sales_per_product, height=350)

    if {"price", "cost", "quantity"}.issubset(df.columns):
        df["revenue"] = df["price"] * df["quantity"]
        df["profit"] = (df["price"] - df["cost"]) * df["quantity"]

        st.subheader("💰 Total Revenue & Profit")

        col1, col2 = st.columns(2)

        col1.metric("Total Revenue", f"Rp {df['revenue'].sum():,.0f}")
        col2.metric("Total Profit", f"Rp {df['profit'].sum():,.0f}")

        fig, ax = plt.subplots()
        sales_per_product.plot(kind="bar", ax=ax)
        ax.set_ylabel("Total Terjual")
        ax.set_xlabel("Produk")
        st.pyplot(fig)

    # ======================
    # AI INSIGHT
    # ======================

    total_rows = df.shape[0]
    total_columns = df.shape[1]
    summary = df.describe(include="all").to_string()

    prompt = f"""
    Berikut adalah ringkasan data penjualan bisnis fashion/retail:

    Jumlah transaksi: {total_rows}
    Jumlah kolom: {total_columns}

    Ringkasan statistik:
    {summary}

    Berikan:
    1. Insight utama dari data
    2. Produk paling potensial
    3. Risiko atau masalah yang terlihat
    4. Rekomendasi strategi bisnis yang konkret
    """

    if st.button("🔎 Analisis dengan AI"):
        with st.spinner("AI sedang menganalisis data..."):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )

            st.subheader("📈 AI Business Insight")
            st.write(chat_completion.choices[0].message.content)
