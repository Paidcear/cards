import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta

# Archivo para la persistencia de datos
FILE_PATH = "tarjetas.json"

# Cargar datos desde JSON
def cargar_datos():
    try:
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Guardar datos en JSON
def guardar_datos(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Determinar tarjetas disponibles con reinicio mensual
def tarjetas_disponibles(data, fecha_actual):
    disponibles = []
    mes_actual = fecha_actual.month
    for tarjeta in data:
        fecha_corte = datetime.strptime(tarjeta["fecha_corte"], "%Y-%m-%d").date()
        
        # Ajustar la fecha de corte para que coincida con el mes actual
        fecha_corte = fecha_corte.replace(month=mes_actual, year=fecha_actual.year)
        
        inicio_disponible = fecha_corte + timedelta(days=1)
        fin_disponible = fecha_corte + timedelta(days=11)
        
        if inicio_disponible <= fecha_actual <= fin_disponible:
            dias_restantes = (fin_disponible - fecha_actual).days
            disponibles.append({
                "Nombre": tarjeta["nombre"],
                "Límite Disponible": tarjeta.get("limite", 0.0),
                "Días Disponibles": dias_restantes
            })
    return disponibles

# Calcular el límite total de crédito
def calcular_limite_total(data):
    return sum(tarjeta.get("limite", 0.0) for tarjeta in data)

# Inicialización de Streamlit
st.set_page_config(page_title="Gestión de Tarjetas de Crédito", layout="wide")
st.title("Gestión de Tarjetas de Crédito")
st.sidebar.title("Menú")

# Cargar datos
datos = cargar_datos()

# Mostrar el límite total de crédito en el panel lateral
limite_total = calcular_limite_total(datos)
st.sidebar.subheader("Límite total de crédito")
st.sidebar.write(f"**${limite_total:,.2f}**")

# Seleccionar opción del menú
opcion = st.sidebar.selectbox("Opciones", ["Panel Principal", "Registrar tarjeta", "Consultar tarjetas disponibles", "Editar tarjeta", "Eliminar tarjeta"])

# Panel principal
if opcion == "Panel Principal":
    st.header("Panel Principal")
    fecha_hoy = st.date_input("Fecha del día", datetime.now().date())
    
    disponibles_hoy = tarjetas_disponibles(datos, fecha_hoy)
    
    st.subheader("Tarjetas disponibles para gastar hoy:")
    if disponibles_hoy:
        # Crear DataFrame de pandas con "Nombre" como índice
        df = pd.DataFrame(disponibles_hoy).set_index("Nombre")
        st.dataframe(df)  # Mostrar tabla dinámica en Streamlit
    else:
        st.write("No hay tarjetas disponibles para gastar hoy.")
