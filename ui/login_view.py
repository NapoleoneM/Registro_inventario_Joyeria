import streamlit as st
import time
import base64
from services.auth import autenticar_usuario

def mostrar_login():
    _, col_logo, _ = st.columns([1, 2, 1])
    with col_logo:
        st.image("assets/5.png", width='stretch')

    with st.container():
        st.markdown("### Iniciar Sesión")
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", type="primary", width='stretch'):
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

    with open("assets/instagramlogo.png", "rb") as _f:
        _ig_b64 = base64.b64encode(_f.read()).decode()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style="text-align:center;">
<details>
  <summary style="cursor:pointer; color:#bbb; font-size:0.68em;
                  list-style:none; -webkit-appearance:none;
                  user-select:none; outline:none;">
    © Napoleone Joyas SAS &nbsp;·&nbsp; Todos los derechos reservados
  </summary>
  <p style="margin-top:10px; color:#aaa; font-size:0.7em; letter-spacing:0.03em;">
    Desarrollado por
  </p>
  <p style="font-size:0.75em; margin-top:4px;">
    <img src="data:image/png;base64,{_ig_b64}" width="13"
         style="vertical-align:middle; margin-right:5px; opacity:0.8;">
    <a href="https://www.instagram.com/camilo_gra67?igsh=MWxmcWFkb2gxYWs2Zw=="
       target="_blank" style="color:#C13584; text-decoration:none;">@camilo_gra67</a>
    &nbsp;&nbsp;&nbsp;
    <img src="data:image/png;base64,{_ig_b64}" width="13"
         style="vertical-align:middle; margin-right:5px; opacity:0.8;">
    <a href="https://www.instagram.com/danielrmrzr?igsh=MXR3aG85NmFpb29xZQ=="
       target="_blank" style="color:#C13584; text-decoration:none;">@danielrmrzr</a>
  </p>
</details>
</div>""",
        unsafe_allow_html=True
    )