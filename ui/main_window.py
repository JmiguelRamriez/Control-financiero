import os
import sys
import re
import shutil
import threading
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import mplcursors

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from tkcalendar import DateEntry
from analyzer import cargar_categorizar_datos, recargar_categorizar_datos, filtrar_mes, calcular_resumen
from agent_ai import responder, responder_consulta_financiera


app = ctk.CTk()
animacion_id = None
cursor_mpl = None
filas_tabla = []
RUTA_DATA = os.path.join(os.path.dirname(__file__), "..", "data")


# Importacion de funciones
df_base = cargar_categorizar_datos()
resumen = calcular_resumen(df_base)
df_actual = df_base
meses_disponibles = sorted(df_base["fecha"].str[:7].unique(), reverse=True)

app.title("FinTracker")
app.geometry("1300x800")
ctk.set_appearance_mode("dark")
app.configure(fg_color="#0a0a1a")

# Tabview
tabview = ctk.CTkTabview(
    app, fg_color="#0a0a1a",
    segmented_button_fg_color="#12122a",
    segmented_button_selected_color="#00E5FF",
    segmented_button_selected_hover_color="#00B8D4",
    segmented_button_unselected_color="#0a0a1a",
    segmented_button_unselected_hover_color="#12122a",
    text_color="white"
)
tabview.pack(fill="both", expand=True, padx=10, pady=8)

tab_dashboard = tabview.add("Dashboard")
tab_dashboard.configure(fg_color="#0a0a1a")

canvas_bg = tk.Canvas(tab_dashboard, highlightthickness=0)
canvas_bg.place(relx=0, rely=0, relwidth=1, relheight=1)

GRADIENT_TOP = "#12122a"
GRADIENT_BOTTOM = "#0a0a1a"
STEPS = 80


def dibujar_gradiente(event=None):
    w = canvas_bg.winfo_width() or 1300
    h = canvas_bg.winfo_height() or 800
    canvas_bg.delete("grad")
    for i in range(STEPS):
        r = int(int(GRADIENT_TOP[1:3], 16) + (int(GRADIENT_BOTTOM[1:3], 16) - int(GRADIENT_TOP[1:3], 16)) * i / STEPS)
        g = int(int(GRADIENT_TOP[3:5], 16) + (int(GRADIENT_BOTTOM[3:5], 16) - int(GRADIENT_TOP[3:5], 16)) * i / STEPS)
        b = int(int(GRADIENT_TOP[5:7], 16) + (int(GRADIENT_BOTTOM[5:7], 16) - int(GRADIENT_TOP[5:7], 16)) * i / STEPS)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y0 = int(i * h / STEPS)
        y1 = int((i + 1) * h / STEPS)
        canvas_bg.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="grad")
    canvas_bg.tag_lower("grad")


canvas_bg.bind("<Configure>", dibujar_gradiente)
app.after(100, dibujar_gradiente)

tab_ai = tabview.add("Asistente IA")
tab_ai.configure(fg_color="#0a0a1a")

# Header
header = ctk.CTkFrame(tab_dashboard, fg_color="transparent")
header.pack(fill="x", padx=10, pady=8)

# titulo
titulo = ctk.CTkLabel(header, text="FinTracker", font=("arial", 20, "bold"))
titulo.pack(side="left", padx=10)

# fecha
fecha = datetime.now().strftime("%d %b %Y")
date = ctk.CTkLabel(header, text=fecha, font=("arial", 20, "bold"))
date.pack(side="right", padx=10)

# frame_cards
frame_cards = ctk.CTkFrame(tab_dashboard, corner_radius=18, fg_color="transparent")
frame_cards.pack(fill="x", padx=10, pady=8)

for i in range(5):
    frame_cards.grid_columnconfigure(i, weight=1)

card1 = ctk.CTkFrame(frame_cards, fg_color="#1a1a3a", border_width=2, border_color="#2a2a5a", corner_radius=18)
card1.grid(row=0, column=0, padx=20, pady=8, sticky="nsew")

card2 = ctk.CTkFrame(frame_cards, fg_color="#1a1a3a", border_width=2, border_color="#2a2a5a", corner_radius=18)
card2.grid(row=0, column=1, padx=20, pady=8, sticky="nsew")

card3 = ctk.CTkFrame(frame_cards, fg_color="#1a1a3a", border_width=2, border_color="#2a2a5a", corner_radius=18)
card3.grid(row=0, column=2, padx=20, pady=8, sticky="nsew")

card4 = ctk.CTkFrame(frame_cards, fg_color="#1a1a3a", border_width=2, border_color="#2a2a5a", corner_radius=18)
card4.grid(row=0, column=3, padx=20, pady=8, sticky="nsew")

card5 = ctk.CTkFrame(frame_cards, fg_color="#1a1a3a", border_width=2, border_color="#2a2a5a", corner_radius=18)
card5.grid(row=0, column=4, padx=20, pady=8, sticky="nsew")

ctk.CTkLabel(card1, text="TOTAL GASTADO", font=("Segoe UI", 11), text_color="#8888aa").pack(pady=3)
label_total = ctk.CTkLabel(
    card1, text=f"${resumen['total_gastado']:.2f}", font=("Segoe UI", 24, "bold")
)
label_total.pack()

ctk.CTkLabel(card2, text="TRANSACCIONES", font=("Segoe UI", 11), text_color="#8888aa").pack(pady=3)
label_transacciones = ctk.CTkLabel(
    card2, text=resumen["transacciones"], font=("Segoe UI", 24, "bold")
)
label_transacciones.pack()

ctk.CTkLabel(card3, text="MAYOR CATEGORIA", font=("Segoe UI", 11), text_color="#8888aa").pack(pady=3)
label_mayor = ctk.CTkLabel(
    card3, text=resumen["mayor_categoria"], font=("Segoe UI", 24, "bold")
)
label_mayor.pack()

ctk.CTkLabel(card4, text="PROMEDIO CATEGORIA", font=("Segoe UI", 11), text_color="#8888aa").pack(pady=3)
label_promedio = ctk.CTkLabel(
    card4, text=f"${resumen['promedio']:.2f}", font=("Segoe UI", 24, "bold")
)
label_promedio.pack()

ctk.CTkLabel(card5, text="INGRESOS TOTALES", font=("Segoe UI", 11), text_color="#8888aa").pack(pady=3)
label_ingresos = ctk.CTkLabel(
    card5, text=f"${resumen['total_ingresos']:.2f}", font=("Segoe UI", 24, "bold")
)
label_ingresos.pack()

categorias_barras = []
barras_progreso = []
labels_pct_barras = []
colores_barra = ["#00E5FF", "#FF2D6B", "#00FF88", "#FFD700", "#BB86FC"]

for i in range(5):
    fb = ctk.CTkFrame(frame_cards, fg_color="#1a1a3a", corner_radius=12,
                      border_width=1, border_color="#2a2a5a")
    fb.grid(row=1, column=i, padx=20, pady=(0, 15), sticky="nsew")
    lb_cat = ctk.CTkLabel(fb, text="", font=("Segoe UI", 10, "bold"), text_color=colores_barra[i])
    lb_cat.pack(pady=(8, 2))
    pb = ctk.CTkProgressBar(fb, height=12, corner_radius=6,
                            fg_color="#0a0a1a", progress_color=colores_barra[i])
    pb.set(0)
    pb.pack(fill="x", padx=10, pady=4)
    lb_pct = ctk.CTkLabel(fb, text="", font=("Segoe UI", 10), text_color="#8888aa")
    lb_pct.pack(pady=(0, 6))
    categorias_barras.append(lb_cat)
    barras_progreso.append(pb)
    labels_pct_barras.append(lb_pct)


def actualizar_barras_progreso(suma_categorias):
    if suma_categorias is None or (hasattr(suma_categorias, 'empty') and suma_categorias.empty) or len(suma_categorias) == 0:
        for lb, pb, lp in zip(categorias_barras, barras_progreso, labels_pct_barras):
            lb.configure(text="")
            pb.set(0)
            lp.configure(text="")
        return
    items = sorted(suma_categorias.items(), key=lambda x: abs(x[1]), reverse=True)
    max_val = abs(items[0][1]) if items else 1
    for i in range(5):
        if i < len(items):
            cat, val = items[i]
            pct = abs(val) / max_val
            categorias_barras[i].configure(text=cat)
            barras_progreso[i].set(pct)
            labels_pct_barras[i].configure(text=f"${abs(val):.0f} ({abs(val) / sum(abs(v) for _, v in items) * 100:.0f}%)")
        else:
            categorias_barras[i].configure(text="")
            barras_progreso[i].set(0)
            labels_pct_barras[i].configure(text="")

actualizar_barras_progreso(resumen["suma_categorias"])

# Filtro por mes
frame_filtros = ctk.CTkFrame(tab_dashboard, fg_color="transparent")
frame_filtros.pack(fill="x", padx=10, pady=8)

ctk.CTkLabel(frame_filtros, text="Mes:", font=("Segoe UI", 12), text_color="#8888aa").pack(side="left", padx=(10, 2))
mes_combo = ctk.CTkOptionMenu(frame_filtros, values=meses_disponibles, fg_color="#1a1a3a",
                              button_color="#00E5FF", button_hover_color="#00B8D4",
                              text_color="white", dropdown_fg_color="#1a1a3a",
                              dropdown_text_color="white", dropdown_hover_color="#2a2a5a")
mes_combo.pack(side="left", padx=(0, 10))


colores_barras = [
    "#00E5FF", "#FF2D6B", "#00FF88", "#FFB300",
    "#7FDBFF", "#FF6B9D", "#BB8FCE", "#85C1E9",
    "#00CED1", "#FF9F43"
]


# Funcion de animacion de la grafica
def animar_barras(datos, frame=0, total_frames=20):
    global animacion_id, cursor_mpl
    altura_final = abs(datos)
    altura_actual = altura_final * (frame / total_frames)
    ax.clear()
    colores = colores_barras[:len(datos.index)]
    altura_actual.plot(
        kind="bar", ax=ax, color=colores, edgecolor="#2a2a5a", width=0.6, linewidth=0.5
    )
    ax.set_ylim(0, altura_final.max() * 1.25)
    ax.set_title("Gastos por categoria", fontsize=13, pad=10)
    ax.set_facecolor("#12122a")
    ax.tick_params(colors="#8888aa", labelsize=10)
    ax.title.set_color("white")
    ax.grid(axis="y", alpha=0.08, color="#2a2a5a", linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#2a2a5a")
    ax.spines["bottom"].set_color("#2a2a5a")
    plt.xticks(rotation=40, ha="right")

    if frame >= total_frames - 1:
        for container in ax.containers:
            ax.bar_label(container, fmt="$%.0f", color="white", fontsize=9, padding=3)
        if cursor_mpl:
            cursor_mpl.remove()
        cursor_mpl = mplcursors.cursor(ax, hover=True)
        cursor_mpl.connect(
            "add", lambda sel: sel.annotation.set_text(
                _formato_tooltip(sel, datos)
            )
        )

    canvas.draw()
    if frame < total_frames:
        animacion_id = app.after(40, animar_barras, datos, frame + 1, total_frames)


def _formato_tooltip(sel, datos):
    idx = sel.index
    if isinstance(idx, (list, tuple)):
        idx = idx[-1]
    try:
        cat = datos.index[idx]
        val = abs(datos.iloc[idx])
        pct = val / abs(datos).sum() * 100
        return f"{cat}: ${val:.2f} ({pct:.1f}%)"
    except Exception:
        return f"${abs(sel.target[1]):.2f}"


# Funcion para filtrar por mes
def aplicar_filtro():
    global animacion_id, df_actual
    if animacion_id:
        app.after_cancel(animacion_id)
        animacion_id = None

    mes = mes_combo.get()
    df_actual = filtrar_mes(df_base, mes)
    nuevo_resumen = calcular_resumen(df_actual)

    if df_actual.empty:
        label_total.configure(text="$0.00")
        label_transacciones.configure(text="0")
        label_mayor.configure(text="Sin datos")
        label_promedio.configure(text="$0.00")
        label_ingresos.configure(text="$0.00")
        ax.clear()
        ax.set_facecolor("#12122a")
        ax.text(0.5, 0.5, "Sin datos para este mes", ha="center", va="center",
                color="#8888aa", fontsize=14, transform=ax.transAxes)
        canvas.draw()
        poblar_tabla(df_actual)
        return

    label_total.configure(text=f"${nuevo_resumen['total_gastado']:.2f}")
    label_transacciones.configure(text=nuevo_resumen["transacciones"])
    label_mayor.configure(text=nuevo_resumen["mayor_categoria"])
    label_promedio.configure(text=f"${nuevo_resumen['promedio']:.2f}")
    label_ingresos.configure(text=f"${nuevo_resumen['total_ingresos']:.2f}")
    poblar_tabla(df_actual)
    animar_barras(nuevo_resumen["suma_categorias"])
    actualizar_barras_progreso(nuevo_resumen["suma_categorias"])


# Funcion para restablecer filtro
def restablecer_filtro():
    global animacion_id, df_actual
    if animacion_id:
        app.after_cancel(animacion_id)
        animacion_id = None

    df_actual = df_base
    label_total.configure(text=f"${resumen['total_gastado']:.2f}")
    label_transacciones.configure(text=resumen["transacciones"])
    label_mayor.configure(text=resumen["mayor_categoria"])
    label_promedio.configure(text=f"${resumen['promedio']:.2f}")
    label_ingresos.configure(text=f"${resumen['total_ingresos']:.2f}")
    poblar_tabla(df_actual)
    animar_barras(resumen["suma_categorias"])
    actualizar_barras_progreso(resumen["suma_categorias"])


def recargar_y_refrescar():
    global df_base, resumen, df_actual, animacion_id, meses_disponibles
    if animacion_id:
        app.after_cancel(animacion_id)
        animacion_id = None
    df_base = recargar_categorizar_datos()
    resumen = calcular_resumen(df_base)
    df_actual = df_base
    meses_disponibles = sorted(df_base["fecha"].str[:7].unique(), reverse=True)
    mes_combo.configure(values=meses_disponibles)
    label_total.configure(text=f"${resumen['total_gastado']:.2f}")
    label_transacciones.configure(text=resumen["transacciones"])
    label_mayor.configure(text=resumen["mayor_categoria"])
    label_promedio.configure(text=f"${resumen['promedio']:.2f}")
    label_ingresos.configure(text=f"${resumen['total_ingresos']:.2f}")
    poblar_tabla(df_actual)
    actualizar_barras_progreso(resumen["suma_categorias"])
    animar_barras(resumen["suma_categorias"])


def subir_pdf():
    ruta = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    if not ruta:
        return
    try:
        shutil.copy2(ruta, RUTA_DATA)
        recargar_y_refrescar()
        pdf_feedback.configure(text="[OK] PDF cargado", text_color="#4ECDC4")


    except Exception as e:
        pdf_feedback.configure(text=f"Error: {e}", text_color="#FF6B6B")
    app.after(3000, lambda: pdf_feedback.configure(text=""))


def exportar_csv():
    df_export = filtrar_por_busqueda(df_actual, search_var.get())
    if df_export.empty:
        return
    ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if not ruta:
        return
    df_export.to_csv(ruta, index=False)
    pdf_feedback.configure(text="[OK] CSV exportado", text_color="#4ECDC4")
    app.after(3000, lambda: pdf_feedback.configure(text=""))


# Boton para filtrar
btn_filtrar = ctk.CTkButton(frame_filtros, text="> Filtrar", command=aplicar_filtro,
                             fg_color="#00E5FF", hover_color="#00B8D4",
                             text_color="#0a0a1a",
                             border_width=0, corner_radius=20)
btn_filtrar.pack(side="left", padx=5)

# Boton para restablecer
btn_restablecer = ctk.CTkButton(
    frame_filtros, text="<< Restablecer", command=restablecer_filtro,
    fg_color="#1a1a3a", hover_color="#12122a", text_color="white",
    border_width=1, border_color="#2a2a5a", corner_radius=20
)
btn_restablecer.pack(side="left", padx=5)

btn_cargar = ctk.CTkButton(
    frame_filtros, text="+ Cargar PDF", command=subir_pdf,
    fg_color="#1a1a3a", hover_color="#12122a", text_color="white",
    border_width=1, border_color="#2a2a5a", corner_radius=20
)
btn_cargar.pack(side="right", padx=5)

btn_exportar = ctk.CTkButton(
    frame_filtros, text=">> Exportar CSV", command=exportar_csv,
    fg_color="#1a1a3a", hover_color="#12122a", text_color="white",
    border_width=1, border_color="#2a2a5a", corner_radius=20
)
btn_exportar.pack(side="right", padx=5)

pdf_feedback = ctk.CTkLabel(frame_filtros, text="", font=("Arial", 12))
pdf_feedback.pack(side="right", padx=(0, 5))

# Grafica de barras
frame_grafica = ctk.CTkFrame(tab_dashboard, corner_radius=18, fg_color="transparent")
frame_grafica.pack(fill="both", expand=True, padx=10, pady=8)


fig, ax = plt.subplots(figsize=(10, 4.2))
fig.patch.set_facecolor("#0a0a1a")

canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

animar_barras(resumen["suma_categorias"])

# Tabla de transacciones
def filtrar_por_busqueda(df, texto):
    if not texto.strip():
        return df
    mask = (
        df["descripcion"].str.contains(texto, case=False, na=False)
        | df["categoria"].str.contains(texto, case=False, na=False)
        | df["banco"].str.contains(texto, case=False, na=False)
    )
    return df[mask]


def on_search_change(*args):
    texto = search_var.get()
    df_filtrado = filtrar_por_busqueda(df_actual, texto)
    poblar_tabla(df_filtrado)


frame_tabla = ctk.CTkFrame(tab_dashboard, corner_radius=18, fg_color="transparent")
frame_tabla.pack(fill="x", padx=10, pady=(0, 10))

frame_tabla_header = ctk.CTkFrame(frame_tabla, fg_color="transparent")
frame_tabla_header.pack(fill="x", padx=15, pady=(10, 5))

ctk.CTkLabel(frame_tabla_header, text="TRANSACCIONES", font=("Segoe UI", 14, "bold")).pack(side="left")

search_var = ctk.StringVar()
search_var.trace_add("write", on_search_change)
search_entry = ctk.CTkEntry(frame_tabla_header, placeholder_text="Buscar...",
                              fg_color="#1a1a3a", border_color="#2a2a5a", text_color="white",
                              textvariable=search_var, width=220, corner_radius=14)
search_entry.pack(side="right")

frame_scroll_tabla = ctk.CTkScrollableFrame(
    frame_tabla, height=180, corner_radius=12,
    scrollbar_fg_color="#0a0a1a",
    scrollbar_button_color="#1a1a3a",
    scrollbar_button_hover_color="#2a2a5a"
)
frame_scroll_tabla.pack(fill="x", padx=10, pady=(0, 10))

columnas = ["Fecha", "Descripcion", "Monto", "Banco", "Categoria"]
anchos = [0.12, 0.43, 0.15, 0.10, 0.20]

frame_encabezado = ctk.CTkFrame(frame_scroll_tabla, fg_color="#12122a")
frame_encabezado.pack(fill="x")
for i, (col, ancho) in enumerate(zip(columnas, anchos)):
    label = ctk.CTkLabel(
        frame_encabezado, text=col, font=("Segoe UI", 12, "bold"),
        anchor="w", width=int(ancho * 600), text_color="white"
    )
    label.grid(row=0, column=i, padx=8, pady=6, sticky="w")
    frame_encabezado.grid_columnconfigure(i, weight=1)


def poblar_tabla(df):
    global filas_tabla
    for f in filas_tabla:
        f.destroy()
    filas_tabla.clear()
    for idx, (_, row) in enumerate(df.iterrows()):
        bg = "#1a1a3a" if idx % 2 == 0 else "#12122a"
        frame_fila = ctk.CTkFrame(frame_scroll_tabla, fg_color=bg)
        frame_fila.pack(fill="x")
        desc = str(row["descripcion"])[:35] if len(str(row["descripcion"])) > 35 else row["descripcion"]
        monto_color = "#FF6B6B" if row["monto"] < 0 else "#4ECDC4"
        monto_txt = f"${abs(row['monto']):.2f}"
        valores = [row["fecha"], desc, monto_txt, row["banco"], row["categoria"]]
        for i, (val, ancho) in enumerate(zip(valores, anchos)):
            color = monto_color if i == 2 else "white"
            label = ctk.CTkLabel(
                frame_fila, text=val, font=("Arial", 11),
                anchor="w", width=int(ancho * 600), text_color=color
            )
            label.grid(row=0, column=i, padx=8, pady=3, sticky="w")
            frame_fila.grid_columnconfigure(i, weight=1)
        filas_tabla.append(frame_fila)


poblar_tabla(df_actual)


# --- TAB AI ---
chat_header = ctk.CTkLabel(tab_ai, text="Asistente Financiero", font=("Segoe UI", 16, "bold"))
chat_header.pack(padx=10, pady=(10, 2))

chat_frame = ctk.CTkScrollableFrame(
    tab_ai, fg_color="#0a0a1a",
    scrollbar_fg_color="#0a0a1a",
    scrollbar_button_color="#1a1a3a",
    scrollbar_button_hover_color="#2a2a5a"
)
chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

frame_preguntas = ctk.CTkFrame(tab_ai, fg_color="transparent")
frame_preguntas.pack(fill="x", padx=10, pady=(0, 5))

frame_input = ctk.CTkFrame(tab_ai, fg_color="transparent")
frame_input.pack(fill="x", padx=10, pady=(0, 10))

entry_mensaje = ctk.CTkEntry(frame_input, placeholder_text="Escribe tu pregunta aqui...",
                               fg_color="#1a1a3a", border_color="#2a2a5a", text_color="white")
entry_mensaje.pack(side="left", fill="x", expand=True, padx=(0, 5))


def markdown_a_plano(texto):
    texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'\*(.*?)\*', r'\1', texto)
    texto = re.sub(r'```[\s\S]*?```', '', texto)
    texto = re.sub(r'`(.*?)`', r'\1', texto)
    texto = re.sub(r'^\|.*\|$', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'^[-*_]{3,}\s*$', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'^\s*[-*+]\s+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'^\s*\d+\.\s+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()


def agregar_burbuja(texto, es_usuario=True):
    frame_burbuja = ctk.CTkFrame(chat_frame, fg_color="transparent")
    frame_burbuja.pack(fill="x", pady=3)

    hora = datetime.now().strftime("%H:%M")
    texto = markdown_a_plano(texto)

    if es_usuario:
        color_fondo = "#00E5FF"
        color_texto = "#0a0a1a"
        anclaje = "e"
        padx = (50, 10)
        color_borde = "#00B8D4"
    else:
        color_fondo = "#1a1a3a"
        color_texto = "white"
        anclaje = "w"
        padx = (10, 50)
        color_borde = "#2a2a5a"

    burbuja = ctk.CTkFrame(
        frame_burbuja, fg_color=color_fondo, corner_radius=16,
        border_width=1, border_color=color_borde
    )
    burbuja.pack(side="right" if es_usuario else "left", padx=padx, pady=2)

    ctk.CTkLabel(
        burbuja, text=texto, font=("Arial", 13),
        text_color=color_texto, wraplength=380, justify="left"
    ).pack(padx=14, pady=(10, 2))

    ctk.CTkLabel(
        burbuja, text=hora, font=("Arial", 9),
        text_color="#999999", anchor=anclaje
    ).pack(padx=14, pady=(0, 6), anchor=anclaje)

    chat_frame._parent_canvas.yview_moveto(1.0)
    return frame_burbuja


def enviar_mensaje():
    mensaje = entry_mensaje.get().strip()
    if not mensaje:
        return
    entry_mensaje.delete(0, "end")
    agregar_burbuja(mensaje, es_usuario=True)

    respuesta_instantanea = responder_consulta_financiera(mensaje)
    if respuesta_instantanea:
        agregar_burbuja(respuesta_instantanea, es_usuario=False)
        return

    typing = agregar_burbuja("...", es_usuario=False)

    def tarea():
        try:
            respuesta = responder(mensaje)
        except Exception as e:
            respuesta = f"Error: {e}"
        app.after(0, typing.destroy)
        app.after(0, lambda: agregar_burbuja(respuesta, es_usuario=False))

    threading.Thread(target=tarea, daemon=True).start()


def enviar_mensaje_texto(texto):
    entry_mensaje.delete(0, "end")
    entry_mensaje.insert(0, texto)
    enviar_mensaje()


preguntas = [
    "¿Cuánto gasté en total?",
    "¿Cuál es mi mayor categoría?",
    "¿Dónde puedo reducir gastos?",
    "¿Resumen de gastos?",
]

for pregunta in preguntas:
    btn = ctk.CTkButton(
        frame_preguntas, text=pregunta, command=lambda t=pregunta: enviar_mensaje_texto(t),
        fg_color="#1a1a3a", hover_color="#12122a", text_color="white",
        border_width=1, border_color="#2a2a5a",
        font=("Segoe UI", 11), height=28, corner_radius=14
    )
    btn.pack(side="left", padx=(0, 6))


btn_enviar = ctk.CTkButton(frame_input, text="Enviar", command=enviar_mensaje,
                            fg_color="#00E5FF", hover_color="#00B8D4",
                            text_color="#0a0a1a",
                            border_width=0, corner_radius=20)
btn_enviar.pack(side="left")

entry_mensaje.bind("<Return>", lambda e: enviar_mensaje())

agregar_burbuja("Bienvenido al asistente financiero. Preguntame sobre tus gastos.", es_usuario=False)


app.mainloop()
