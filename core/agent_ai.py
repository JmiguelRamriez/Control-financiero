import os
import re
from datetime import datetime
from openai import OpenAI
from analyzer import (
    cargar_categorizar_datos,
    calcular_resumen,
    filtrar_mes,
    filtrar_por_dia,
)

API_KEY = os.getenv("NVIDIA_API_KEY", "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")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=API_KEY,
)

df_base = cargar_categorizar_datos()
resumen_global = calcular_resumen(df_base)


def responder_consulta_financiera(mensaje):
    msg = mensaje.lower()
    r = resumen_global

    if "total" in msg and ("gast" in msg or "gaste" in msg):
        return f"El total gastado es ${r['total_gastado']:.2f}"

    if "ingreso" in msg or "gane" in msg or "recibi" in msg:
        return f"El total de ingresos es ${r['total_ingresos']:.2f}"

    if "balance" in msg or "saldo" in msg:
        return f"El balance actual es ${r['balance']:.2f}"

    if "ultima" in msg or "ultimo" in msg or "reciente" in msg:
        ultimas = df_base.tail(5)
        lineas = "\n".join(
            f"- {row['fecha']} | {row['descripcion'][:30]} | ${abs(row['monto']):.2f}"
            for _, row in ultimas.iterrows()
        )
        return f"Ultimas transacciones:\n{lineas}"

    if "transaccion" in msg or "movimiento" in msg:
        return f"Hay {r['transacciones']} transacciones en total"

    if "mayor" in msg and ("categoria" in msg or "categoría" in msg or "gasto" in msg):
        return f"La categoria con mayor gasto es {r['mayor_categoria']}"

    if "promedio" in msg and "categoria" in msg:
        return f"El promedio de gasto por categoria es ${r['promedio']:.2f}"

    if "categoria" in msg and ("gasto" in msg or "gastos" in msg):
        lineas = "\n".join(
            f"- {cat}: ${abs(monto):.2f}" for cat, monto in r["suma_categorias"].items()
        )
        return f"Gastos por categoria:\n{lineas}"

    for cat in ["comida", "transporte", "supermercado", "entretenimiento", "belleza"]:
        if cat in msg:
            for categoria, monto in r["suma_categorias"].items():
                if categoria.lower() == cat:
                    return f"Gastaste ${abs(monto):.2f} en {categoria}"
            return f"No hay gastos registrados en {cat}"

    match_mes = re.search(
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        msg,
    )
    if match_mes:
        meses_map = {
            "enero": "01",
            "febrero": "02",
            "marzo": "03",
            "abril": "04",
            "mayo": "05",
            "junio": "06",
            "julio": "07",
            "agosto": "08",
            "septiembre": "09",
            "octubre": "10",
            "noviembre": "11",
            "diciembre": "12",
        }
        mes_num = meses_map[match_mes.group(1)]
        match_anio = re.search(r"(\d{4})", msg)
        anio = match_anio.group(1) if match_anio else str(datetime.now().year)
        year_mes = f"{anio}-{mes_num}"
        df_mes = filtrar_mes(df_base, year_mes)
        if df_mes.empty:
            return f"No hay datos para {match_mes.group(1)} de {anio}"
        r_mes = calcular_resumen(df_mes)
        return (
            f"En {match_mes.group(1)} de {anio}:\n"
            f"- Total gastado: ${r_mes['total_gastado']:.2f}\n"
            f"- Total ingresos: ${r_mes['total_ingresos']:.2f}\n"
            f"- Balance: ${r_mes['balance']:.2f}\n"
            f"- Transacciones: {r_mes['transacciones']}\n"
            f"- Mayor categoria: {r_mes['mayor_categoria']}\n"
            f"- Promedio por categoria: ${r_mes['promedio']:.2f}"
        )

    match_dia = re.search(r"(\d{4})-(\d{2})-(\d{2})", msg)
    if match_dia:
        dia = match_dia.group(0)
        df_dia = filtrar_por_dia(df_base, dia)
        if df_dia.empty:
            return f"No hay datos para el dia {dia}"
        r_dia = calcular_resumen(df_dia)
        return (
            f"El dia {dia}:\n"
            f"- Total gastado: ${r_dia['total_gastado']:.2f}\n"
            f"- Total ingresos: ${r_dia['total_ingresos']:.2f}\n"
            f"- Balance: ${r_dia['balance']:.2f}\n"
            f"- Transacciones: {r_dia['transacciones']}\n"
            f"- Mayor categoria: {r_dia['mayor_categoria']}"
        )

    return None


def responder(mensaje):
    respuesta_local = responder_consulta_financiera(mensaje)
    if respuesta_local:
        return respuesta_local

    if not API_KEY:
        return (
            "El asistente AI no esta disponible. Configura la variable NVIDIA_API_KEY."
        )

    categorias_str = "\n".join(
        f"- {cat}: ${abs(monto):.2f}"
        for cat, monto in resumen_global["suma_categorias"].items()
    )

    system_prompt = (
        "Eres un asistente financiero experto. "
        "Estos son los datos financieros actuales del usuario:\n\n"
        f"RESUMEN GENERAL:\n"
        f"- Total gastado: ${resumen_global['total_gastado']:.2f}\n"
        f"- Total ingresos: ${resumen_global['total_ingresos']:.2f}\n"
        f"- Balance: ${resumen_global['balance']:.2f}\n"
        f"- Transacciones: {resumen_global['transacciones']}\n"
        f"- Mayor categoria de gasto: {resumen_global['mayor_categoria']}\n"
        f"- Promedio por categoria: ${resumen_global['promedio']:.2f}\n\n"
        f"GASTOS POR CATEGORIA:\n{categorias_str}\n\n"
        "Con base en estos datos, responde preguntas y da recomendaciones "
        "financieras personalizadas. Se concreto y util."
    )
    try:
        completion = client.chat.completions.create(
            model="minimaxai/minimax-m2.7",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje},
            ],
            temperature=1,
            top_p=0.95,
            max_tokens=1024,
            stream=False,
        )
        msg = completion.choices[0].message
        reasoning = getattr(msg, "reasoning", None) or getattr(msg, "reasoning_content", None)
        response = msg.content
        if reasoning:
            response = f"[Razonamiento]\n{reasoning}\n\n[Respuesta]\n{response}"
        return response
    except Exception as e:
        return f"Error al conectar con el asistente: {e}"


if __name__ == "__main__":
    while True:
        mensaje = input("\nQue deseas preguntar? (escribe 'salir' para terminar)\n")
        if mensaje.lower() == "salir":
            break
        print(responder(mensaje))
