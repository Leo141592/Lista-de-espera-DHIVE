import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
# refrescar cada segundo
st_autorefresh(interval=1000, key="contador")
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
    ahora = datetime.now()

    impresiones = df[df["Impresora"] == impresora_seleccionada]

    st.subheader(f"Estado de {impresora_seleccionada}")

    if impresiones.empty:

        st.success("Estado: Libre")
        st.write("Tiempo hasta que termine la impresión: 0")
        st.write("Hora de finalización: -")
        st.write("Impresiones en cola: 0")
        st.write("Tiempo total restante: 0")
        st.write("Hora hasta disponibilidad: Ahora")

    else:

        impresiones = impresiones.copy()

        impresiones["Hora final impresión"] = pd.to_datetime(
            impresiones["Hora final impresión"],
            format="%H:%M:%S"
        ).apply(lambda x: ahora.replace(
            hour=x.hour,
            minute=x.minute,
            second=x.second
        ))

        impresiones = impresiones.sort_values("Hora final impresión")

        actual = impresiones.iloc[0]

        tiempo_restante = actual["Hora final impresión"] - ahora

        if tiempo_restante.total_seconds() < 0:
            tiempo_restante = timedelta(seconds=0)

        horas = tiempo_restante.seconds // 3600
        minutos = (tiempo_restante.seconds % 3600) // 60
        segundos = tiempo_restante.seconds % 60

        cola = len(impresiones) - 1

        ultima = impresiones.iloc[-1]["Hora final impresión"]

        tiempo_total = ultima - ahora
        if tiempo_total.total_seconds() < 0:
            tiempo_total = timedelta(seconds=0)

        h_total = tiempo_total.seconds // 3600
        m_total = (tiempo_total.seconds % 3600) // 60
        s_total = tiempo_total.seconds % 60

        st.error("Estado: Imprimiendo")

        st.write(
            f"Tiempo hasta que termine la impresión: "
            f"{horas}h {minutos}m {segundos}s"
        )

        st.write(
            f"Hora de finalización: "
            f"{actual['Hora final impresión'].strftime('%H:%M:%S')}"
        )

        st.write(f"Impresiones en cola: {cola}")

        st.write(
            f"Tiempo total restante: "
            f"{h_total}h {m_total}m {s_total}s"
        )

        st.write(
            f"Hora hasta disponibilidad: "
            f"{ultima.strftime('%H:%M:%S')}"
        )# ----------------------------------
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