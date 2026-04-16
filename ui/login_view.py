import streamlit as st
import time
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
                        # --- 1. SI EL USUARIO ENTRA, RESETEAMOS LA TRAMPA ---
                        st.session_state['intentos_fallidos'] = 0
                        
                        # --- GUARDAMOS LOS DATOS EN LA MEMORIA ---
                        st.session_state.logueado = True
                        st.session_state.usuario_logueado = nombre_aux
                        st.session_state.sheet_asignado = sheet_id
                        st.rerun() # Recargamos para entrar a la app
                    else:
                        # --- 2. SI EL USUARIO FALLA, ACTIVAMOS LA TRAMPA ---
                        st.session_state['intentos_fallidos'] += 1
                        
                        if st.session_state['intentos_fallidos'] >= 3:
                            # Lo bloqueamos por 60 segundos (puedes ajustar este número)
                            st.session_state['bloqueado_hasta'] = time.time() + 60
                            st.warning("Demasiados intentos fallidos. Sistema de seguridad activado.")
                            st.rerun() # Forzamos la recarga para que main.py lo bloquee
                        else:
                            # Calculamos cuántas oportunidades le quedan
                            intentos_restantes = 3 - st.session_state['intentos_fallidos']
                            st.error(f"{nombre_aux} | Te quedan {intentos_restantes} intentos.")
            else:
                st.warning("Por favor ingrese usuario y contraseña.")