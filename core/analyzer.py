import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loader import df_total, fecha_a_iso

# Diccionario para encontrar las categorias
categorias = {
    "didi": "Transporte",
    "tacos": "Comida",
    "oxxo": "Convivencia",
    "heb": "Supermercado",
    "mc donald": "Comida",
    "barberia": "Belleza",
    "super q": "Convivencia",
    "food": "Comida",
    "apple": "Suscripciones",
    "amazon": "Compras en linea",
    "mercado libre": "Compras en linea",
    "pago": "Abono",
    "soriana": "Supermercado",
    "hamburgesas": "Comida",
    "temu": "Compras en linea",
    "disposiciòn": "Transferencia",
    "transferencia": "Transferencia",
    "gusanos": "Comida",
    "uber": "Transporte",
    "recarga": "Transporte",
    "Mcdonalds": "Comida",
    "rest": "Comida",
    "Disposición": "Transferencia",
    "Hamburguerzo": "Comida",
    "vel pay": "Belleza",
    "disposición": "Transferencia",
    "hamburguerzo": "Comida",
    "carnic": "Comida",
    "cremeria": "Comida",
    "paseo": "Entretenimiento",
    "th tec": "Comida",
}


# Funcion para categorizar
def categorizar_desc(descripcion):
    desc_lower = descripcion.lower()
    for keyword, categoria in categorias.items():
        if keyword in desc_lower:
            return categoria
    else:
        return "otros"


# Filtrado de mes
def filtrar_mes(df, year_mes):
    return df[df["fecha"].str[:7] == year_mes]


# Filtrado de dia
def filtrar_por_dia(df, dia_exacto):
    return df[df["fecha"] == dia_exacto]


def cargar_categorizar_datos():
    df = df_total.copy()
    df["categoria"] = df["descripcion"].apply(categorizar_desc)
    return df


def calcular_resumen(df):
    solo_gastos = df[df["monto"] < 0]
    solo_gastos = solo_gastos[solo_gastos["categoria"] != "Abono"]
    suma_categorias = solo_gastos.groupby("categoria")["monto"].sum()

    return {
        "total_gastado": abs(solo_gastos["monto"].sum()),
        "transacciones": len(df),
        "mayor_categoria": suma_categorias.idxmin(),
        "promedio": abs(suma_categorias.mean()),
        "gastos": solo_gastos,
        "suma_categorias": suma_categorias,
    }


if __name__ == "__main__":
    df = cargar_categorizar_datos()
    resumen = calcular_resumen(df)
