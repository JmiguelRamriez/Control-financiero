import pandas as pd
import re
import pdfplumber
import os
import glob


meses = {
    "ENE": "01",
    "FEB": "02",
    "MAR": "03",
    "ABR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AGO": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DIC": "12",
}


def fecha_a_iso(regex):
    partes = regex.split()
    dia = partes[0]
    mes = meses[partes[1]]
    anio = partes[2]
    return f"{anio}-{mes}-{dia}"


def fecha_plata_a_iso(fecha_str):
    partes = fecha_str.split("-")
    dia = partes[0]
    mes = meses[partes[1].upper()]  # Convertimos 'may' a 'MAY'
    anio = partes[2]
    return f"{anio}-{mes}-{dia}"


def monto_float(regex):
    signo = -1.0 if regex[0] == "+" else 1.0
    limpio = regex.replace("+", "").replace("-", "").replace("$", "").replace(",", "")
    monto = float(limpio)

    return signo * monto


regex = re.compile(
    r"^(\d{2}\s+\w{3}\s+\d{4})"
    r"\s+"
    r"(\d{2}\s+\w{3}\s+\d{4})"
    r"\s+"
    r"(.+?)"  # descripción (lazy)
    r"\s*\|\s*RFC:\s*S\.I\."
    r"\s+([-+]\$[\d,]+\.?\d*)"
)

regex_plata = re.compile(
    r"^(\d{2}-[a-z]{3}-\d{4})\s+"  # Grupo 1: Fecha (ej. 11-may-2026)
    r"\d{2}-[a-z]{3}-\d{4}\s+"  # Ignora la Fecha de cargo
    r"[\wX]{16}\s+"  # Ignora el número de tarjeta (ej. 531722XXXXXX5062)
    r"(.+?)(?=\s+[+-]\s+\d)"  # Grupo 2: Descripción del movimiento
    r".*?\$([\d,]+\.\d{2})"  # Grupo 3: Salta todo hasta encontrar el $ final y captura el monto
)


def leer_nu(ruta_pdf):
    filas = []
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()

            # Si la página está vacía, saltamos a la siguiente
            if not texto:
                continue

            # CORRECCIÓN 1: Esta línea ahora está alineada con el 'if', no debajo del 'continue'
            for linea in texto.split("\n"):
                match = regex.match(linea)
                if match:
                    fecha, _, descripcion, monto = match.groups()
                    filas.append(
                        {
                            "fecha": fecha_a_iso(fecha),
                            "descripcion": descripcion.strip(),
                            "monto": monto_float(monto),
                            "banco": "nu",
                        }
                    )
    return pd.DataFrame(filas)


def leer_plata(ruta_pdf):
    filas = []
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if not texto:
                continue

            for linea in texto.split("\n"):
                match = regex_plata.match(linea)
                if match:
                    fecha, descripcion, monto = match.groups()

                    limpio = monto.replace(",", "")
                    valor_monto = float(limpio)

                    if (
                        "Pago por transferencia" in descripcion
                        or "Cashback" in descripcion
                    ):
                        valor_monto = abs(valor_monto)  # Ingreso
                    else:
                        valor_monto = -abs(valor_monto)  # Gasto

                    filas.append(
                        {
                            "fecha": fecha_plata_a_iso(fecha),
                            "descripcion": descripcion.strip(),
                            "monto": valor_monto,
                            "banco": "plata",
                        }
                    )
    return pd.DataFrame(filas)


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def detectar_formato(ruta_pdf):
    with pdfplumber.open(ruta_pdf) as pdf:
        texto = pdf.pages[0].extract_text() if pdf.pages else ""
    if not texto:
        return None
    if re.search(r"\d{2}\s+[A-Z]{3}\s+\d{4}", texto):
        return "nu"
    if re.search(r"\d{2}-[a-z]{3}-\d{4}", texto):
        return "plata"
    return None


def cargar_todos_pdfs():
    dfs = []
    for pdf in glob.glob(os.path.join(DATA_DIR, "*.pdf")):
        fmt = detectar_formato(pdf)
        if fmt == "nu":
            df = leer_nu(pdf)
        elif fmt == "plata":
            df = leer_plata(pdf)
        else:
            continue
        if not df.empty:
            dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


df_total = cargar_todos_pdfs()
