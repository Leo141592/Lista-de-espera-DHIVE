import streamlit as st

st.title("Mi primera app con Streamlit")

st.write("Hola mundo 👋")

nombre = st.text_input("¿Cómo te llamas?")

if nombre:
    st.write(f"Hola {nombre}")