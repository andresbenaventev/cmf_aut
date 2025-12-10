# -*- coding: utf-8 -*-

import math
import pandas as pd
import streamlit as st
import io
from io import BytesIO

# Cuentas objetivo
CUENTAS_OBJETIVO = [
    "Ingresos de actividades ordinarias",
    "Deudores comerciales y otras cuentas por cobrar corrientes",
]
UMBRAL_USD = 40_000_000

# Configuración de la página
st.set_page_config(page_title="Informe IFRS - Empresas Grandes", layout="centered")
st.title("📊 Análisis de Empresas IFRS")
st.markdown("""
1. Descarga el último informe desde:  
   👉 [CMF - Estadísticas IFRS](https://www.cmfchile.cl/institucional/estadisticas/estadisticas_ifrs.php)

2. Luego, sube el archivo `.txt` que descargaste.

3. Ingresa el valor del dólar usado en el informe.

4. El sistema filtrará las empresas con ingresos o cuentas por cobrar sobre 40 millones USD.
""")

# Función para limpiar caracteres especiales y tildes
def limpiar_texto(text):
    reemplazos = {
        "ñ": "n", "Ñ": "N",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "'": "", "´": "",
    }
    for original, nuevo in reemplazos.items():
        text = str(text).replace(original, nuevo)
    return text

# Subir archivo
archivo = st.file_uploader("📂 Subir archivo .txt del informe IFRS", type=["txt"])

# Ingresar valor del dólar
valor_dolar = st.number_input("💵 Valor del dólar (CLP por USD)", min_value=100.0, max_value=2000.0, step=1.0)

def formato_contable(valor):
    try:
        return f"${valor:,.0f}"
    except:
        return valor


if archivo and valor_dolar:
    # Leer archivo con codificación latinoamericana
    contenido = archivo.read().decode("utf-8", errors="replace")
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

    # Limpiar caracteres especiales en todas las columnas de texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(limpiar_texto)

    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")

    # Convertir CLP a USD
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

    # Crear tabla pivot con las dos cuentas
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

    # Mostrar resultados
    st.success(f"✅ Se encontraron {len(resultado)} empresas sobre {UMBRAL_USD:,} USD.")
    # Clonar para no modificar el original
    preview = resultado.copy()
    
    # Aplicar formato contable a columnas numéricas
    for col in ["ingresos_usd", "deudores_usd", "max_usd"]:
        if col in preview.columns:
            preview[col] = preview[col].apply(formato_contable)
    
    st.dataframe(preview)


    # Guardar a Excel en memoria
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        resultado.to_excel(writer, index=False, sheet_name="Empresas")
    
        workbook  = writer.book
        worksheet = writer.sheets["Empresas"]
    
        # Formato contable
        formato_contable = workbook.add_format({
            'num_format': '_($* #,##0_);_($* (#,##0);_($* "-"??_);_(@_)',
            'align': 'right'
        })
    
        # Detectar columnas numéricas a formatear
        columnas_a_formatear = ["ingresos_usd", "deudores_usd", "max_usd"]
        for idx, col in enumerate(resultado.columns):
            # Ajustar ancho
            max_len = max(resultado[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(idx, idx, max_len)
    
            # Si es columna numérica, aplicar formato contable
            if col in columnas_a_formatear:
                worksheet.set_column(idx, idx, max_len, formato_contable)
    
    output.seek(0)


    # Botón de descarga
    st.download_button(
        label="💾 Descargar resultado en Excel",
        data=output,
        file_name="empresas_grandes_ifrs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
