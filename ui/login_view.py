import streamlit as st
from services.auth import autenticar_usuario

def mostrar_login():
    st.title("🦁💍 Napoleone Joyas - Acceso")
    
    with st.container():
        st.markdown("### Iniciar Sesión")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            if usuario and password:
                with st.spinner("Validando credenciales..."):
                    exito, nombre_aux, sheet_id = autenticar_usuario(usuario, password)
                    
                    if exito:
                        # --- GUARDAMOS LOS DATOS EN LA MEMORIA ---
                        st.session_state.logueado = True
                        st.session_state.usuario_logueado = nombre_aux
                        st.session_state.sheet_asignado = sheet_id # <--- CLAVE PARA EL ENRUTAMIENTO
                        st.rerun() # Recargamos para entrar a la app
                    else:
                        st.error(nombre_aux) # Muestra el mensaje de error ("Inactivo", "Incorrecto")
            else:
                st.warning("Por favor ingrese usuario y contraseña.")