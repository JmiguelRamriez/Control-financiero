import os
import pandas as pd
from loader import leer_plata, leer_nu


def guardar_historial(df, ruta):
    df.to_csv(ruta, index=False)


def cargar_historial(ruta):
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    else:
        return pd.DataFrame(
            columns=["fecha", "descripcion", "monto", "banco", "categoria"]
        )


bancos = {"nu": leer_nu, "plata": leer_plata}


def actualizar_historial(ruta, nombre_banco, ruta_historial):
    historial = cargar_historial(ruta_historial)
    df_nuevo = bancos[nombre_banco](ruta)
    resultado = pd.concat([historial, df_nuevo], ignore_index=True)
    resultado = resultado.drop_duplicates()
    guardar_historial(resultado, ruta_historial)
    return resultado


df = actualizar_historial(
    "/home/josemr21/Proyectos/Python/finances/data/Estado de cuenta 12 may – 9 jun.pdf",
    "plata",
    "/home/josemr21/Proyectos/Python/finances/data/historial.csv",
)
print(df)
