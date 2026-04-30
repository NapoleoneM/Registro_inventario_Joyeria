import streamlit as st
import time
from PIL import Image
from ui.login_view import mostrar_login
from ui.form_view import mostrar_formulario

# Configuración básica de la pestaña del navegador
st.set_page_config(page_title="Registros Auxiliares", page_icon=Image.open("assets/favicon.ico"))

def main():
    # 1. Inicializar variables de sesión básicas y de seguridad
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
    if 'intentos_fallidos' not in st.session_state:
        st.session_state['intentos_fallidos'] = 0
    if 'bloqueado_hasta' not in st.session_state:
        st.session_state['bloqueado_hasta'] = 0

    # Lógica de ruteo
    if st.session_state['usuario_logueado'] is None:
        
        # --- BARRERA DE SEGURIDAD (LOCKOUT) ---
        tiempo_actual = time.time()
        if tiempo_actual < st.session_state['bloqueado_hasta']:
            tiempo_restante = int(st.session_state['bloqueado_hasta'] - tiempo_actual)
            st.error(f"🚨 Por seguridad, sistema bloqueado. Espera {tiempo_restante} segundos para volver a intentar.")
            return # Detiene la ejecución aquí, ocultando el formulario de login
        # --------------------------------------
        
        mostrar_login()
    else:
        mostrar_formulario()
        
        # Agregamos un botón en la barra lateral para salir
        st.sidebar.markdown("---")
        if st.sidebar.button("Cerrar Sesión", width='stretch'):
            st.session_state['usuario_logueado'] = None
            st.rerun()

if __name__ == "__main__":
    main()