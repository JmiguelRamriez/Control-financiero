import pandas as pd
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


def recargar_categorizar_datos():
    """Recarga todos los PDFs del disco y devuelve datos frescos categorizados."""
    from loader import cargar_todos_pdfs
    df = cargar_todos_pdfs()
    df["categoria"] = df["descripcion"].apply(categorizar_desc)
    return df


def calcular_resumen(df):
    solo_gastos = df[df["monto"] < 0]
    solo_gastos = solo_gastos[solo_gastos["categoria"] != "Abono"]
    solo_ingresos = df[df["monto"] > 0]

    total_ingresos = solo_ingresos["monto"].sum()
    total_gastado = abs(solo_gastos["monto"].sum()) if not solo_gastos.empty else 0
    balance = total_ingresos - total_gastado

    if solo_gastos.empty:
        return {
            "total_gastado": 0,
            "total_ingresos": total_ingresos,
            "balance": balance,
            "transacciones": len(df),
            "mayor_categoria": "N/A",
            "promedio": 0,
            "gastos": solo_gastos,
            "suma_categorias": solo_gastos.groupby("categoria")["monto"].sum(),
        }

    suma_categorias = solo_gastos.groupby("categoria")["monto"].sum()

    return {
        "total_gastado": total_gastado,
        "total_ingresos": total_ingresos,
        "balance": balance,
        "transacciones": len(df),
        "mayor_categoria": suma_categorias.idxmin(),
        "promedio": abs(suma_categorias.mean()),
        "gastos": solo_gastos,
        "suma_categorias": suma_categorias,
    }


if __name__ == "__main__":
    df = cargar_categorizar_datos()
    resumen = calcular_resumen(df)
    print("=== FinTracker - Analyzer ===")
    print(f"Total gastado: ${resumen['total_gastado']:.2f}")
    print(f"Total ingresos: ${resumen['total_ingresos']:.2f}")
    print(f"Balance: ${resumen['balance']:.2f}")
    print(f"Transacciones: {resumen['transacciones']}")
    print(f"Mayor categoria: {resumen['mayor_categoria']}")
    print(f"Promedio por categoria: ${resumen['promedio']:.2f}")
