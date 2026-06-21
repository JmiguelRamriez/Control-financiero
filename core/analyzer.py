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


# Filtrado de año
def filtrar_por_dia(df, dia_exacto):
    return df[df["fecha"] == dia_exacto]


df_total["categoria"] = df_total["descripcion"].apply(categorizar_desc)
df_sum = df_total.groupby("categoria")["monto"].sum()
gastos = df_sum[df_sum < 0]


# DEBUG
print("Filtrado de dia")
print(filtrar_por_dia(df_total, "2026-05-11"))

print("filtrado de mes")
print(filtrar_mes(df_total, "2026-05"))

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
gastos.abs().plot(kind="bar", ax=ax1)

ax1.set_title("GASTOS")
ax1.set_xlabel("CATEGORIAS")
ax1.set_ylabel("GASTO")

# Gráfica de pie
gastos.abs().plot(kind="pie", ax=ax2, autopct="%1.1f%%")
ax2.set_title("GASTOS")

plt.tight_layout()
plt.show()
