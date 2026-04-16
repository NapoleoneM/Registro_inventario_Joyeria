import streamlit as st
from ui.login_view import mostrar_login
from ui.form_view import mostrar_formulario

# Configuración básica de la pestaña del navegador
st.set_page_config(page_title="Registros Auxiliares", page_icon="📝🦁")

def main():
    # Inicializar la variable de sesión si es la primera vez que entra
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None

    # Lógica de ruteo
    if st.session_state['usuario_logueado'] is None:
        mostrar_login()
    else:
        mostrar_formulario()
        
        # Agregamos un botón en la barra lateral para salir
        st.sidebar.markdown("---")
        if st.sidebar.button("Cerrar Sesión", use_container_width=True):
            st.session_state['usuario_logueado'] = None
            st.rerun()

if __name__ == "__main__":
    main()