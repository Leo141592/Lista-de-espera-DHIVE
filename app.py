import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# ----------------------------------
# CONFIGURACION ARCHIVO DE DATOS
# ----------------------------------

DATA_FILE = "lista_espera.csv"

COLUMNAS = [
    "Carnet",
    "Nombre",
    "Telefono",
    "Hora inicio impresión",
    "Hora final impresión",
    "Tiempo de impresión",
    "Impresora",
    "Estado"
]

# ----------------------------------
# CREAR CSV SI NO EXISTE
# ----------------------------------

if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
    df_inicial = pd.DataFrame(columns=COLUMNAS)
    df_inicial.to_csv(DATA_FILE, index=False)

# ----------------------------------
# FUNCIONES
# ----------------------------------

def cargar_datos():
    return pd.read_csv(DATA_FILE)

def guardar_datos():
    st.session_state.lista_espera.to_csv(DATA_FILE, index=False)

# ----------------------------------
# INICIALIZAR SESSION STATE
# ----------------------------------

if "lista_espera" not in st.session_state:
    st.session_state.lista_espera = cargar_datos()

# ----------------------------------
# CONFIGURACION PAGINA
# ----------------------------------

st.set_page_config(page_title="Sistema de Impresiones", layout="wide")

st.title("Sistema de Gestión de Impresiones")

tab1, tab2, tab3, tab4 = st.tabs([
    "Lista de espera",
    "Impresoras",
    "Impresiones",
    "Personas"
])

# ----------------------------------
# TAB 1 - LISTA DE ESPERA
# ----------------------------------

with tab1:

    st.header("Lista de espera")

    st.dataframe(
        st.session_state.lista_espera,
        use_container_width=True
    )

# ----------------------------------
# TAB 2 - IMPRESORAS
# ----------------------------------

with tab2:

    st.header("Impresoras")

    impresoras = [
        "H2D",
        "P1S Azul",
        "P1S Naranja",
        "P1S Amarilla",
        "A1 mini"
    ]

    impresora_seleccionada = st.selectbox(
        "Selecciona una impresora",
        impresoras
    )

    df = st.session_state.lista_espera

    impresiones = df[df["Impresora"] == impresora_seleccionada]

    ahora = datetime.now()

    if impresiones.empty:

        st.subheader("Estado: 🟢 Libre")
        st.write("No hay impresiones registradas.")

    else:

        # convertir horas
        impresiones = impresiones.copy()
        impresiones["Hora final dt"] = impresiones["Hora final impresión"].apply(
            lambda x: ahora.replace(
                hour=int(x.split(":")[0]),
                minute=int(x.split(":")[1]),
                second=int(x.split(":")[2])
            )
        )

        impresiones = impresiones.sort_values("Hora final dt")

        actual = None
        cola = []

        for _, row in impresiones.iterrows():

            if row["Hora final dt"] > ahora and actual is None:
                actual = row
            elif actual is not None:
                cola.append(row)

        if actual is None:

            st.subheader("Estado: 🟢 Libre")
            st.write("No hay impresiones en progreso.")

        else:

            tiempo_restante = actual["Hora final dt"] - ahora

            horas = tiempo_restante.seconds // 3600
            minutos = (tiempo_restante.seconds % 3600) // 60

            st.subheader("Estado: 🔴 Imprimiendo")

            st.write(f"**Tiempo hasta terminar impresión:** {horas}h {minutos}m")

            st.write(
                f"**Hora de finalización:** {actual['Hora final dt'].strftime('%H:%M:%S')}"
            )

        # cola de impresiones
        st.subheader("Impresiones en cola")

        if len(cola) == 0:

            st.write("No hay impresiones en cola.")

        else:

            cola_df = pd.DataFrame(cola)
            st.dataframe(
                cola_df[["Carnet", "Nombre", "Tiempo de impresión"]],
                use_container_width=True
            )

        # calcular disponibilidad total

        ultima = impresiones["Hora final dt"].max()

        tiempo_total = ultima - ahora

        horas_total = tiempo_total.seconds // 3600
        minutos_total = (tiempo_total.seconds % 3600) // 60

        st.subheader("Resumen total")

        st.write(f"**Tiempo total restante:** {horas_total}h {minutos_total}m")

        st.write(
            f"**Hora hasta disponibilidad:** {ultima.strftime('%H:%M:%S')}"
        )
# ----------------------------------
# TAB 3 - IMPRESIONES
# ----------------------------------

with tab3:

    st.header("Registrar impresión")

    with st.form("form_impresion"):

        carnet = st.text_input("Carnet")
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")

        tiempo = st.number_input(
            "Tiempo de impresión (minutos)",
            min_value=1
        )

        impresora = st.selectbox(
            "Impresora",
            ["H2D", "P1S Azul", "P1S Naranja", "P1S Amarilla", "A1 mini"]
        )

        submitted = st.form_submit_button("Guardar impresión")

        if submitted:

            hora_inicio = datetime.now()
            tiempo_total = tiempo + 5
            hora_final = hora_inicio + timedelta(minutes=tiempo_total)

            estado = "Imprimiendo"

            df = st.session_state.lista_espera

            # revisar si la impresora está ocupada
            impresiones_impresora = df[df["Impresora"] == impresora]

            if not impresiones_impresora.empty:

                ultima_hora = impresiones_impresora["Hora final impresión"].iloc[-1]

                ultima_hora = datetime.strptime(ultima_hora, "%H:%M:%S")

                ultima_hora = hora_inicio.replace(
                    hour=ultima_hora.hour,
                    minute=ultima_hora.minute,
                    second=ultima_hora.second
                )

                if hora_inicio < ultima_hora:
                    estado = "En espera"

            nueva_fila = {
                "Carnet": carnet,
                "Nombre": nombre,
                "Telefono": telefono,
                "Hora inicio impresión": hora_inicio.strftime("%H:%M:%S"),
                "Hora final impresión": hora_final.strftime("%H:%M:%S"),
                "Tiempo de impresión": tiempo,
                "Impresora": impresora,
                "Estado": estado
            }

            st.session_state.lista_espera.loc[
                len(st.session_state.lista_espera)
            ] = nueva_fila

            guardar_datos()

            if estado == "Imprimiendo":
                st.success("La impresión comenzó inmediatamente")
            else:
                st.warning("La impresora está ocupada. La impresión quedó en espera.")

# ----------------------------------
# TAB 4 - PERSONAS
# ----------------------------------

with tab4:

    st.header("Personas")

    st.write("Gestión de usuarios que utilizan el sistema.")