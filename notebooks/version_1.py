
import pandas as pd
import os

def ejecutar():

    # Leer archivo CSV
    df = pd.read_csv("notebooks/data/csv/shopping_behavior_2023.csv")

    # Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Filtrar métodos de pago
    df = df[df["payment_method"] == "PayPal"]

    # Filtrar frecuencia de compras
    df = df[df["frequency_of_purchases"].isin(
        ["Weekly", "Fortnightly", "bi-weekly"]
    )]

    # Agrupar y sumar compras
    df = (
        df[["customer_id", "category", "purchase_amount_(usd)"]]
        .groupby(["customer_id", "category"])
        .sum()
        .reset_index()
    )

    # Calcular ranking
    df["rank"] = df.groupby("category")[
        "purchase_amount_(usd)"
    ].rank(method="dense", ascending=False)

    # Obtener los primeros lugares
    df = df[df["rank"] == 1]

    # Obtener resultados
    values = df[["customer_id", "category"]].to_dict()

    customers = list(values["customer_id"].values())
    categories = list(values["category"].values())

    result = list(zip(customers, categories))

    # Generar archivo de resultados
    with open("result.txt", "w") as f:
        for customer_id, category in result:
            f.write(f"{customer_id}, {category}\n")

    print("Pipeline versión 1 ejecutado correctamente")

    return result
