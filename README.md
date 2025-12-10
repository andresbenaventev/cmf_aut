# cmf_aut
# 📊 IFRS Empresas - Análisis de Estados Financieros

Esta es una aplicación web que permite analizar los estados financieros publicados por la CMF (Comisión para el Mercado Financiero de Chile) bajo normativa IFRS, y filtrar las empresas que tienen ingresos o cuentas por cobrar por sobre los 40 millones de USD.

## 🚀 ¿Qué hace esta app?

1. Te guía para descargar el último informe IFRS desde el sitio de la CMF.
2. Te permite subir el archivo `.txt` descargado.
3. Pide el valor del dólar del período correspondiente.
4. Procesa los datos y te muestra:
   - Ingresos ordinarios en USD
   - Deudores comerciales en USD
   - Un resumen filtrado de empresas grandes
5. Puedes descargar el resultado como archivo CSV.

## 🔗 Link a la página de informes CMF

👉 [https://www.cmfchile.cl/institucional/estadisticas/estadisticas_ifrs.php](https://www.cmfchile.cl/institucional/estadisticas/estadisticas_ifrs.php)

## 🧑‍💻 Cómo usar la app

### Opción 1: Desde Streamlit Cloud

> Si estás viendo esto en GitHub, puedes usar la app directamente sin instalar nada.  
Haz clic aquí para abrir la app (una vez desplegada):  
📎 https://YOUR-STREAMLIT-URL.streamlit.app

### Opción 2: Ejecutar localmente

1. Instala las dependencias:

```bash
pip install -r requirements.txt

