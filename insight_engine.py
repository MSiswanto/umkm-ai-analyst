def generate_insight(df, question):
    q = question.lower()

    df["revenue"] = df["price"] * df["quantity"]
    df["profit"] = (df["price"] - df["cost"]) * df["quantity"]

    if "turun" in q:
        trend = df.groupby("date")["revenue"].sum()
        if trend.iloc[-1] < trend.iloc[0]:
            return "Revenue menunjukkan tren menurun. Disarankan cek kompetitor atau lakukan promo terbatas."
        else:
            return "Revenue tidak menunjukkan penurunan signifikan."

    elif "profit" in q:
        top_profit = df.groupby("product_name")["profit"].sum().idxmax()
        return f"Produk dengan kontribusi profit terbesar adalah {top_profit}. Fokus scale produk ini."

    elif "produk rugi" in q:
        loss_products = df.groupby("product_name")["profit"].sum()
        loss = loss_products[loss_products < 0]
        if not loss.empty:
            return f"Produk yang merugi: {', '.join(loss.index)}. Pertimbangkan naikkan harga atau hentikan."
        else:
            return "Tidak ada produk yang merugi."

    else:
        return "Coba tanyakan tentang tren, profit, atau produk merugi."
