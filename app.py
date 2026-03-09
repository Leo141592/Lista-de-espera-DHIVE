import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema de Impresiones", layout="wide")

st.title("Sistema de Gestión de Impresiones")

tab1, tab2, tab3, tab4 = st.tabs([
    "Lista de espera",
    "Impresoras",
    "Impresiones",
    "Personas"
])

# ---------------------------
# TAB 1 - LISTA DE ESPERA
# ---------------------------
with tab1:

    st.header("Lista de espera")

    # Datos iniciales (ejemplo)
    data = {
        "Carnet": [],
        "Nombre": [],
        "Telefono": [],
        "Hora inicio impresión": [],
        "Hora final impresión": [],
        "Tiempo de impresión": [],
        "Impresora": [],
        "Estado": []
    }

    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)
# ---------------------------
# TAB 2 - IMPRESORAS
# ---------------------------
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

    st.subheader(f"Información de la impresora: {impresora_seleccionada}")

    st.write("Aquí podrás mostrar el estado, cola y estadísticas de esta impresora.")
# ---------------------------
# TAB 3
# ---------------------------
with tab3:
    st.header("Impresiones")

    st.write("Registro de impresiones realizadas.")

# ---------------------------
# TAB 4
# ---------------------------
with tab4:
    st.header("Personas")

    st.write("Gestión de usuarios que utilizan el sistema.")