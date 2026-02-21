def pricing_recommendation(cost, comp_low, comp_high, target_margin):
    penetration_price = comp_low - 500
    optimal_price = cost * (1 + target_margin / 100)
    premium_price = comp_high + 1000

    strategy = """
    📌 Strategi:
    - Gunakan penetration price untuk masuk pasar.
    - Gunakan optimal price untuk keseimbangan margin & volume.
    - Gunakan premium price jika brand sudah kuat.
    """

    return {
        "Penetration Price": penetration_price,
        "Optimal Price": round(optimal_price),
        "Premium Price": premium_price,
        "Strategy": strategy
    }
