# Versión 2 --COMPLETA-- JCDM

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
                "Nombre Tarjeta": tarjeta["nombre"],
                #"Límite Disponible": tarjeta.get("limite", 0.0),
                "Días Disponibles": dias_restantes,
                "Fecha de Pago": tarjeta.get("fecha_pago")
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
    #fecha_pago = st.date_input("Fecha de pago")
    
    disponibles_hoy = tarjetas_disponibles(datos, fecha_hoy)
    
    st.subheader("Tarjetas disponibles para gastar hoy:")
    if disponibles_hoy:
        # Crear DataFrame de pandas con "Nombre" como índice
        df = pd.DataFrame(disponibles_hoy).set_index("Nombre Tarjeta")
        st.dataframe(df)  # Mostrar tabla dinámica en Streamlit
    else:
        st.write("No hay tarjetas disponibles para gastar hoy.")


# Registrar tarjeta
elif opcion == "Registrar tarjeta":
    st.header("Registrar una nueva tarjeta")

    nombre = st.text_input("Nombre de la tarjeta")
    dia_corte = st.number_input("Día de corte del mes (1-31)", min_value=1, max_value=31)
    dia_pago = st.number_input("Día de pago del mes (1-31)", min_value=1, max_value=31)
    limite = st.number_input("Límite total disponible", min_value=0.0, step=0.01)

    if st.button("Guardar tarjeta"):
        # Se crea la fecha de corte y pago para el primer mes (el mes actual)
        fecha_corte = datetime(datetime.now().year, datetime.now().month, dia_corte).strftime("%Y-%m-%d")
        fecha_pago = datetime(datetime.now().year, datetime.now().month, dia_pago).strftime("%Y-%m-%d")

        nueva_tarjeta = {
            "nombre": nombre,
            "fecha_corte": fecha_corte,
            "fecha_pago": fecha_pago,
            "limite": limite
        }
        datos.append(nueva_tarjeta)
        guardar_datos(datos)
        st.success("Tarjeta registrada correctamente.")

# Consultar tarjetas disponibles
elif opcion == "Consultar tarjetas disponibles":
    st.header("Consultar tarjetas disponibles")

    tarjeta_seleccionada = st.selectbox("Selecciona una tarjeta", ["Todas"] + [tarjeta["nombre"] for tarjeta in datos])

    if tarjeta_seleccionada == "Todas":
        # Filtro de búsqueda
        filtro = st.text_input("Filtrar tarjetas por nombre")

        # Filtrar las tarjetas que coincidan con el texto ingresado
        tarjetas_filtradas = [tarjeta for tarjeta in datos if filtro.lower() in tarjeta["nombre"].lower()]

        # Ordenar las tarjetas alfabéticamente
        tarjetas_filtradas.sort(key=lambda tarjeta: tarjeta["nombre"])

        # Mostrar las tarjetas filtradas y ordenadas
        if tarjetas_filtradas:
            st.write("Tarjetas disponibles para gastar:")
            st.table(tarjetas_filtradas)
        else:
            st.write("No hay tarjetas disponibles para esta fecha o no coinciden con el filtro.")

    else:
        tarjeta = next(t for t in datos if t["nombre"] == tarjeta_seleccionada)
        st.subheader("Detalles de la tarjeta seleccionada:")
        st.write(f"**Nombre:** {tarjeta['nombre']}")
        st.write(f"**Fecha de corte:** {tarjeta['fecha_corte']}")
        st.write(f"**Fecha de pago:** {tarjeta['fecha_pago']}")
        st.write(f"**Límite total disponible:** ${tarjeta.get('limite', 0.0):.2f}")

# Editar tarjeta
elif opcion == "Editar tarjeta":
    st.header("Editar información de una tarjeta")

    nombres_tarjetas = [tarjeta["nombre"] for tarjeta in datos]
    tarjeta_seleccionada = st.selectbox("Selecciona la tarjeta a editar", nombres_tarjetas)

    if tarjeta_seleccionada:
        tarjeta = next(t for t in datos if t["nombre"] == tarjeta_seleccionada)
        nuevo_nombre = st.text_input("Nuevo nombre", tarjeta["nombre"])
        nuevo_dia_corte = st.number_input("Nuevo día de corte", value=int(tarjeta["fecha_corte"].split("-")[2]), min_value=1, max_value=31)
        nuevo_dia_pago = st.number_input("Nuevo día de pago", value=int(tarjeta["fecha_pago"].split("-")[2]), min_value=1, max_value=31)
        nuevo_limite = st.number_input("Nuevo límite total disponible", value=tarjeta.get("limite", 0.0), min_value=0.0, step=0.01)

        if st.button("Guardar cambios"):
            # Actualizar la fecha de corte y de pago para el mes actual
            nueva_fecha_corte = datetime(datetime.now().year, datetime.now().month, nuevo_dia_corte).strftime("%Y-%m-%d")
            nueva_fecha_pago = datetime(datetime.now().year, datetime.now().month, nuevo_dia_pago).strftime("%Y-%m-%d")

            tarjeta["nombre"] = nuevo_nombre
            tarjeta["fecha_corte"] = nueva_fecha_corte
            tarjeta["fecha_pago"] = nueva_fecha_pago
            tarjeta["limite"] = nuevo_limite

            guardar_datos(datos)
            st.success("Tarjeta actualizada correctamente.")

# Eliminar tarjeta
elif opcion == "Eliminar tarjeta":
    st.header("Eliminar tarjeta")

    nombres_tarjetas = [tarjeta["nombre"] for tarjeta in datos]
    tarjeta_seleccionada = st.selectbox("Selecciona la tarjeta a eliminar", nombres_tarjetas)

    if tarjeta_seleccionada:
        if st.button("Eliminar tarjeta"):
            tarjeta_a_eliminar = next(t for t in datos if t["nombre"] == tarjeta_seleccionada)
            datos.remove(tarjeta_a_eliminar)
            guardar_datos(datos)
            st.success("Tarjeta eliminada correctamente.")
