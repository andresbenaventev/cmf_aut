# -*- coding: utf-8 -*-

import math
import pandas as pd
import streamlit as st
import io
from io import BytesIO
import unicodedata

# Constantes
CUENTAS_OBJETIVO = [
    "Ingresos de actividades ordinarias",
    "Deudores comerciales y otras cuentas por cobrar corrientes",
]
UMBRAL_USD = 40_000_000

# Normalizar texto: eliminar tildes y convertir "ñ" → "n"
def normalizar_texto(text):
    try:
        texto = unicodedata.normalize("NFKD", str(text))
        texto = texto.encode("ascii", "ignore").decode("utf-8")
        return texto
    except:
        return text

# Configuración de la app
st.set_page_config(page_title="Informe IFRS - Empresas Grandes", layout="centered")
st.title("📊 Análisis de Empresas IFRS")
st.markdown("""
1. Descarga el último informe desde:
   👉 [CMF - Estadísticas IFRS](https://www.cmfchile.cl/institucional/estadisticas/estadisticas_ifrs.php)

2. Luego, sube el archivo `.txt` que descargaste.

3. Ingresa el valor del dólar usado en el informe.

4. El sistema filtrará las empresas con ingresos o cuentas por cobrar **sobre 40 millones USD**.
""")

# Subir archivo
archivo = st.file_uploader("📂 Subir archivo .txt del informe IFRS", type=["txt"])

# Ingresar valor del dólar
valor_dolar = st.number_input("💵 Valor del dólar (CLP por USD)", min_value=100.0, max_value=2000.0, step=1.0)

if archivo and valor_dolar:
    contenido = archivo.read().decode("latin-1", errors="replace")

    df = pd.read_csv(
        io.StringIO(contenido),
        sep=";",
        header=None,
        names=[
            "periodo", "codigo_entidad", "nombre_entidad", "tipo",
            "moneda", "cuenta", "monto", "taxonomia", "origen"
        ],
        dtype=str
    )

    # Normalizar todas las columnas de texto (quita ñ y tildes)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(normalizar_texto)

    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")

    # Convertir a USD
    def convertir(row):
        if pd.isna(row["monto"]):
            return math.nan
        if row["moneda"] == "CLP":
            return row["monto"] / valor_dolar
        elif row["moneda"] == "USD":
            return row["monto"]
        return math.nan

    df = df[df["cuenta"].isin(CUENTAS_OBJETIVO)].copy()
    df["monto_usd"] = df.apply(convertir, axis=1)

    # Pivot table
    tabla = df.pivot_table(
        index=["codigo_entidad", "nombre_entidad"],
        columns="cuenta",
        values="monto_usd",
        aggfunc="first"
    ).reset_index()

    tabla = tabla.rename(columns={
        "Ingresos de actividades ordinarias": "ingresos_usd",
        "Deudores comerciales y otras cuentas por cobrar corrientes": "deudores_usd"
    })

    tabla["max_usd"] = tabla[["ingresos_usd", "deudores_usd"]].max(axis=1)
    resultado = tabla[tabla["max_usd"] >= UMBRAL_USD].sort_values("max_usd", ascending=False)

    # Mostrar resultado
    st.success(f"✅ Se encontraron {len(resultado)} empresas sobre {UMBRAL_USD:,} USD.")
    st.dataframe(resultado)

    # Exportar a Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        resultado.to_excel(writer, index=False, sheet_name="Empresas")

    output.seek(0)
    st.download_button(
        label="💾 Descargar resultado en Excel",
        data=output,
        file_name="empresas_grandes_ifrs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
