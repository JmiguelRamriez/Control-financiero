import customtkinter as ctk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

app = ctk.CTk()
app.title("FinTracker")
app.geometry("1200x700")
ctk.set_appearance_mode("dark")

# Header
header = ctk.CTkFrame(app)
header.pack(fill="x", padx=10, pady=5)

# titulo
titulo = ctk.CTkLabel(header, text="FinTracker", font=("arial", 20, "bold"))
titulo.pack(side="left", padx=10)

# fecha
fecha = datetime.now().strftime("%d %b %Y")
date = ctk.CTkLabel(header, text=fecha, font=("arial", 20, "bold"))
date.pack(side="right", padx=10)

# frame_cards
frame_cards = ctk.CTkFrame(app)
frame_cards.pack(fill="x", padx=10, pady="5")

for i in range(4):
    frame_cards.grid_columnconfigure(i, weight=1)

# creacion de las cartas
card1 = ctk.CTkFrame(frame_cards)
card1.grid(
    row=0,
    column=0,
    padx=50,
    pady=10,
    sticky="nsew",
)

card2 = ctk.CTkFrame(frame_cards)
card2.grid(row=0, column=1, padx=50, pady=10, sticky="nsew")

card3 = ctk.CTkFrame(frame_cards)
card3.grid(row=0, column=2, padx=50, pady=10, sticky="nsew")

card4 = ctk.CTkFrame(frame_cards)
card4.grid(row=0, column=3, padx=50, pady=10, sticky="nsew")

# Poner las cartas en el grid
ctk.CTkLabel(card1, text="TOTAL GASTADO", font=("arial", 12)).pack(pady=5)
ctk.CTkLabel(card1, text="$0.00", font=("Arial", 24, "bold")).pack()

ctk.CTkLabel(card2, text="Transacciones", font=("arial", 12)).pack(pady=5)
ctk.CTkLabel(card2, text="$0.00", font=("Arial", 24, "bold")).pack()

ctk.CTkLabel(card3, text="Mayor categoria", font=("arial", 12)).pack(pady=5)
ctk.CTkLabel(card3, text="$0.00", font=("Arial", 24, "bold")).pack()

ctk.CTkLabel(card4, text="Promdio", font=("arial", 12)).pack(pady=5)
ctk.CTkLabel(card4, text="$0.00", font=("Arial", 24, "bold")).pack()

frame_grafica = ctk.CTkFrame(app)
frame_grafica.pack(fill="both", expand=True, padx=10, pady=5)

app.mainloop()
