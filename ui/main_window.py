import os
import sys
from tkinter import Entry
from matplotlib import text
import mplcursors

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from tkcalendar import DateEntry
from analyzer import cargar_categorizar_datos, filtrar_por_dia, calcular_resumen


app = ctk.CTk()
animacion_id = None
cursor_mpl = None


# Importacion de funciones
df_base = cargar_categorizar_datos()
resumen = calcular_resumen(df_base)

app.title("FinTracker")
app.geometry("1300x800")
ctk.set_appearance_mode("dark")

# Header
header = ctk.CTkFrame(app, fg_color="transparent")
header.pack(fill="x", padx=10, pady=5)

# titulo
titulo = ctk.CTkLabel(header, text="FinTracker", font=("arial", 20, "bold"))
titulo.pack(side="left", padx=10)

# fecha
fecha = datetime.now().strftime("%d %b %Y")
date = ctk.CTkLabel(header, text=fecha, font=("arial", 20, "bold"))
date.pack(side="right", padx=10)

# frame_cards
frame_cards = ctk.CTkFrame(app, corner_radius=5)
frame_cards.pack(fill="x", padx=10, pady=5)

for i in range(4):
    frame_cards.grid_columnconfigure(i, weight=1)

# creacion de las cartas
card1 = ctk.CTkFrame(frame_cards)
card1.grid(row=0, column=0, padx=50, pady=10, sticky="nsew")

card2 = ctk.CTkFrame(frame_cards)
card2.grid(row=0, column=1, padx=50, pady=15, sticky="nsew")

card3 = ctk.CTkFrame(frame_cards)
card3.grid(row=0, column=2, padx=50, pady=15, sticky="nsew")

card4 = ctk.CTkFrame(frame_cards)
card4.grid(row=0, column=3, padx=50, pady=15, sticky="nsew")

# Poner las cartas en el grid
# TOTAL gastado
ctk.CTkLabel(card1, text="TOTAL GASTADO", font=("arial", 12)).pack(pady=5)
label_total = ctk.CTkLabel(
    card1, text=f"${resumen['total_gastado']:.2f}", font=("Arial", 24, "bold")
)
label_total.pack()

# Numero de transacciones
ctk.CTkLabel(card2, text="Numero de transacciones", font=("arial", 12)).pack(pady=5)
label_transacciones = ctk.CTkLabel(
    card2, text=resumen["transacciones"], font=("Arial", 24, "bold")
)
label_transacciones.pack()

# Categoria en la que mas se gasto
ctk.CTkLabel(card3, text="Mayor categoria", font=("arial", 12)).pack(pady=5)
label_mayor = ctk.CTkLabel(
    card3, text=resumen["mayor_categoria"], font=("Arial", 24, "bold")
)
label_mayor.pack()

# El promedio de gasto por categoria
ctk.CTkLabel(card4, text="Promedio por categoria", font=("arial", 12)).pack(pady=5)
label_promedio = ctk.CTkLabel(
    card4, text=resumen["promedio"], font=("Arial", 24, "bold")
)
label_promedio.pack()

# Calendario
frame_filtros = ctk.CTkFrame(app, fg_color="transparent")
frame_filtros.pack(fill="x", padx=10, pady=5)

entry_fecha = DateEntry(frame_filtros, date_pattern="yyyy-mm-dd")
entry_fecha.pack(side="left", padx=10)


# Funcion de animacion de la grafica
def animar_barras(datos, frame=0, total_frames=20):
    global animacion_id, cursor_mpl
    altura_final = abs(datos)
    altura_actual = altura_final * (frame / total_frames)
    ax.clear()
    altura_actual.plot(
        kind="bar", ax=ax, color="#60A5FA", edgecolor="#2b2b2b", width=0.6
    )
    ax.set_ylim(0, altura_final.max() * 1.15)
    ax.set_title("Gastos por categoria")
    ax.set_facecolor("#2b2b2b")
    ax.tick_params(colors="white")
    ax.title.set_color("white")
    plt.xticks(rotation=45, ha="right")

    if frame >= total_frames - 1:
        if cursor_mpl:
            cursor_mpl.remove()
        cursor_mpl = mplcursors.cursor(ax, hover=True)
        cursor_mpl.connect(
            "add", lambda sel: sel.annotation.set_text(f"${sel.target[1]:.2f}")
        )

    canvas.draw()
    if frame < total_frames:
        animacion_id = app.after(40, animar_barras, datos, frame + 1, total_frames)


# Funcion para filtrar la fecha
def aplicar_filtro():
    global animacion_id
    if animacion_id:
        app.after_cancel(animacion_id)
        animacion_id = None

    fecha = entry_fecha.get()
    df_filtrado = filtrar_por_dia(df_base, fecha)
    nuevo_resumen = calcular_resumen(df_filtrado)
    # Actualiza las cartas
    label_total.configure(text=f"${nuevo_resumen['total_gastado']:.2f}")
    label_transacciones.configure(text=nuevo_resumen["transacciones"])
    label_mayor.configure(text=nuevo_resumen["mayor_categoria"])
    label_promedio.configure(text=f"${nuevo_resumen['promedio']:.2f}")

    # Actualiza la Grafica con animacion
    animar_barras(nuevo_resumen["suma_categorias"])


# Boton para filtrar
btn_filtrar = ctk.CTkButton(frame_filtros, text="Filtrar", command=aplicar_filtro)
btn_filtrar.pack(side="left", padx=10)

# Grafica de barras
frame_grafica = ctk.CTkFrame(app)
frame_grafica.pack(fill="both", expand=True, padx=10, pady=5)


fig, ax = plt.subplots(figsize=(10, 4))
fig.patch.set_facecolor("#2b2b2b")

canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

animar_barras(resumen["suma_categorias"])


app.mainloop()
