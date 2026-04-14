import streamlit as st
from datetime import datetime
from services.google_sheets import agregar_registro, limpiar_registros

# --- FUNCIÓN DE UTILIDAD PARA FORMATEO ---
def formato_decimal_sheets(valor):
    if valor is None or valor == 0.0 or valor == "": return ""
    return str(valor).replace(".", ",")

# --- FUNCIÓN PARA LIMPIAR SOLO LOS DATOS SECUNDARIOS ---
def limpiar_formulario_parcial():
    text_keys = ['in_talla', 'in_set1', 'in_set2', 'in_creativo', 'in_adicional', 'pop_col', 'pop_pano', 'pop_celda']
    for k in text_keys:
        if k in st.session_state: st.session_state[k] = ""
            
    sel_keys = ['in_rec1', 'in_rec2', 'in_broche', 'in_genero', 'in_ubicacion']
    for k in sel_keys:
        if k in st.session_state: st.session_state[k] = "Seleccione..."
            
    # Piedra ahora es una lista vacía por defecto
    if 'in_piedra' in st.session_state: st.session_state['in_piedra'] = []
    if 'in_coleccion' in st.session_state: st.session_state['in_coleccion'] = "Ninguna"
        
    float_keys = ['in_peso', 'in_peso2', 'in_cm_ob', 'in_mm', 'in_cm_op', 'in_setd']
    for k in float_keys:
        if k in st.session_state: st.session_state[k] = 0.0
            
    int_keys = ['in_desc', 'in_costo']
    for k in int_keys:
        if k in st.session_state: st.session_state[k] = 0

def mostrar_formulario():
    # --- MEMORIA Y SEGURIDAD ---
    if 'pop_col' not in st.session_state: st.session_state.pop_col = ""
    if 'pop_pano' not in st.session_state: st.session_state.pop_pano = ""
    if 'pop_celda' not in st.session_state: st.session_state.pop_celda = ""
    if 'hoja_limpia' not in st.session_state: st.session_state.hoja_limpia = False

    # --- INICIALIZACIÓN OBLIGATORIA DE VARIABLES ---
    peso = peso_2 = cm_oblig = cm_opc = grosor_mm = set_d_cm = 0.0
    costo_manual = descuento = 0
    recargo_1 = recargo_2 = broche = genero = coleccion = creativo = ubicacion = talla_anillo = set_c_1 = set_c_2 = adicional = ""
    piedra = [] # Lista obligatoria para el multiselect

    # --- UI: AUXILIAR EN LA PARTE SUPERIOR ---
    auxiliar_actual = st.session_state.get('usuario_logueado', 'Desconocido')
    st.markdown(f"## 👤 {auxiliar_actual}")
    st.markdown("## Registro inventario de Joyería 🦁")
    st.markdown("*Campos obligatorios según selección")
    st.divider()

    # Listas
    opc_modelo = ["Seleccione...", "Pesado", "Oferta", "Pulsera Combo", "Con Piedra", "Piercing", "Fabricación"]
    opc_categoria_base = ["Seleccione...", "Anillo", "Anillo Tejido", "Bola", "Broche", "Cadena", "Candongas", "Dije", "Herraje", "Piercing", "Pulsera Tejida", "Pulso", "Pulso Modulable", "Pulso Bebé", "Rosario", "Tobillera", "Topos", "Set", "Set Cadena y Dije", "Rosca de Seguridad"]
    opc_broche = ["Seleccione...", "No tiene", "Reasa", "Broche", "Nudo Corredizo"]
    opc_genero = ["Seleccione...", "Hombre", "Mujer", "Unisex"]
    opc_coleccion = ["Ninguna", "Italian Chunky", "Tienda de Letras", "Zodiaco", "Emojis", "Futboleros"]
    opc_piedras_disp = ["Esmeralda", "Diamante", "Zafiro", "Rubí"]
    opc_ubicacion = ["Seleccione...", "Bodega 429 Medellin", "Mostrador 424 Medellin", "Ofi. Piso 3° Medellin", "Santafe CC Medellin", "Cosacut CC Cucuta", "Local 7 Cali", "Local 568 Cali", "Mezanine 648 Cali", "Chipichape CC Cali", "Unicentro CC Cali", "USA-M", "USA-C", "USA", "Feria Effix Med"]
    colores_oro = ["Seleccione...", "Oro Amarillo", "Oro Blanco", "Oro Rosa", "Dos Oros Amarillo Blanco", "Dos Oros Amarillo Rosa", "Dos Oros Blanco Rosa", "Dos Oros Negro Amarillo", "Dos Oros Negro Rosa", "Dos Oros Negro Blanco", "Tres Oros"]
    colores_plata = ["Seleccione...", "Plata", "Plata Rodinada", "Plata Vermeil", "Plata Rosé"]
    recargos_oro = ["Seleccione...", "Recargo +1", "Recargo +2", "Recargo +3", "Recargo +4", "Nacional Corriente", "Nacional Especial", "Oro 14K Italiano"]
    recargos_plata = ["Seleccione...", "Plata 925", "Plata 950"]
    
    errores_validacion = []

    col1, col2 = st.columns(2)
    with col1:
        material = st.selectbox("Material *", ["Seleccione...", "Oro", "Plata"], key="sel_mat")
        if material == "Seleccione...": errores_validacion.append("Material")
        
    with col2:
        if material == "Oro":
            qts_ley = st.selectbox("Qts | Ley *", ["Seleccione...", "18K", "14K", "10K"], key="sel_qts_o")
            color_oro = st.selectbox("Color Oro *", colores_oro, key="sel_col_o")
            lista_recargos = recargos_oro 
            if qts_ley == "Seleccione...": errores_validacion.append("Qts | Ley")
            if color_oro == "Seleccione...": errores_validacion.append("Color Oro")
        elif material == "Plata":
            qts_ley = st.selectbox("Qts | Ley *", ["925"], key="sel_qts_p")
            color_oro = st.selectbox("Color Oro *", colores_plata, key="sel_col_p")
            lista_recargos = recargos_plata 
            if color_oro == "Seleccione...": errores_validacion.append("Color Oro")
        else:
            qts_ley = st.selectbox("Qts | Ley", ["Esperando Material..."], disabled=True, key="sel_qts_d")
            color_oro = st.selectbox("Color Oro", ["Esperando Material..."], disabled=True, key="sel_col_d")

    col3, col4 = st.columns(2)
    with col3:
        modelo_precio = st.selectbox("Modelo de Precio *", opc_modelo, key="sel_mod")
        if modelo_precio == "Seleccione...": errores_validacion.append("Modelo de Precio")
    with col4:
        # --- LÓGICA DE CATEGORÍA CONDICIONAL A OFERTA ---
        if modelo_precio == "Oferta":
            opc_categoria = ["Set Cadena y Dije"]
        else:
            opc_categoria = opc_categoria_base
            
        categoria = st.selectbox("Categoría *", opc_categoria, key="sel_cat")
        if categoria == "Seleccione...": errores_validacion.append("Categoría")

    st.divider()

    if material != "Seleccione..." and modelo_precio != "Seleccione..." and categoria != "Seleccione...":
        
        st.subheader("Datos Financieros y Pesos")
        c_fin1, c_fin2, c_fin3 = st.columns(3)
        if modelo_precio in ["Pesado", "Fabricación", "Pulsera Combo", "Piercing", "Oferta", "Con Piedra"]:
            with c_fin1:
                peso = st.number_input("Peso (gr) *", min_value=0.0, step=0.1, format="%0.2f", key="in_peso")
                if peso <= 0: errores_validacion.append("Peso (gr)")
            with c_fin2:
                recargo_1 = st.selectbox("Recargo (Normal) *", lista_recargos, key="in_rec1")
                if recargo_1 == "Seleccione...": errores_validacion.append("Recargo Normal")

        if modelo_precio == "Oferta":
            st.info("Atributos de Oferta Activados")
            c_of1, c_of2, c_of3 = st.columns(3)
            with c_of1:
                peso_2 = st.number_input("Peso Set 2 (gr) *", min_value=0.0, step=0.1, format="%0.2f", key="in_peso2")
                if peso_2 <= 0: errores_validacion.append("Peso Set 2")
            with c_of2:
                recargo_2 = st.selectbox("Recargo (Solo Set 2) *", lista_recargos, key="in_rec2")
                if recargo_2 == "Seleccione...": errores_validacion.append("Recargo Solo Set 2")
            with c_of3:
                descuento = st.number_input("Descuento % * (Solo números)", min_value=0, step=1, format="%d", key="in_desc")
                if descuento <= 0: errores_validacion.append("Descuento %")

        if modelo_precio == "Con Piedra":
            st.info("Atributos de Piedra Activados")
            c_pi1, c_pi2 = st.columns(2)
            with c_pi1:
                costo_manual = st.number_input("Costo Manual * (Valor entero)", min_value=0, step=1000, format="%d", key="in_costo")
                if costo_manual <= 0: errores_validacion.append("Costo Manual")
            with c_pi2:
                # --- MULTISELECT PARA PIEDRA ---
                piedra = st.multiselect("Piedra *", opc_piedras_disp, key="in_piedra")
                if len(piedra) == 0: errores_validacion.append("Piedra (Debe elegir al menos una)")

        st.subheader("Diseño y Medidas")
        cat_cuello_muneca = ["Cadena", "Pulso", "Pulsera Tejida", "Pulso Bebé", "Rosario", "Tobillera", "Set Cadena y Dije"]
        cat_dedo = ["Anillo", "Anillo Tejido"]
        cat_volumen = ["Bola", "Topos"]
        cat_complementarias_medida = ["Candongas", "Dije", "Herraje", "Piercing"]

        c_med1, c_med2, c_med3 = st.columns(3)
        with c_med1:
            if categoria in cat_cuello_muneca or categoria in cat_complementarias_medida or categoria == "Pulso Modulable":
                cm_oblig = st.number_input("(cm) Obligatorio *", min_value=0.0, step=0.5, key="in_cm_ob")
                if cm_oblig <= 0: errores_validacion.append("(cm) Obligatorio")
        with c_med2:
            if categoria in cat_cuello_muneca or categoria in cat_volumen or categoria == "Pulso Modulable":
                grosor_mm = st.number_input("(mm) Grosor *", min_value=0.0, step=0.1, key="in_mm")
                if grosor_mm <= 0: errores_validacion.append("(mm) Grosor")
        with c_med3:
            if categoria in cat_dedo:
                talla_anillo = st.text_input("Talla (Anillos) *", key="in_talla")
                if not talla_anillo: errores_validacion.append("Talla Anillos")
        
        if categoria == "Pulso Modulable":
            cm_opc = st.number_input("(cm) Opcional (Opcional)", min_value=0.0, step=0.5, key="in_cm_op")

        es_set = (categoria == "Set Cadena y Dije")

        if es_set:
            st.info("Medidas de Set Activadas")
            c_set1, c_set2, c_set3 = st.columns(3)
            with c_set1:
                set_c_1 = st.text_input("Set Crea. 1 *", key="in_set1")
                if not set_c_1: errores_validacion.append("Set Crea. 1")
            with c_set2:
                set_c_2 = st.text_input("Set Crea. 2 *", key="in_set2")
                if not set_c_2: errores_validacion.append("Set Crea. 2")
            with c_set3:
                set_d_cm = st.number_input("Set D. cm *", min_value=0.0, step=0.5, key="in_setd")
                if set_d_cm <= 0: errores_validacion.append("Set D. cm")

        st.subheader("Atributos Generales")
        c_gen1, c_gen2, c_gen3 = st.columns(3)
        with c_gen1:
            broche = st.selectbox("Broche *", opc_broche, key="in_broche")
            if broche == "Seleccione...": errores_validacion.append("Broche")
            genero = st.selectbox("Género *", opc_genero, key="in_genero")
            if genero == "Seleccione...": errores_validacion.append("Género")
            
        with c_gen2:
            # --- LÓGICA CORREGIDA PARA "CREATIVO" CONDICIONAL ---
            if es_set:
                lbl_crea = "Creativo (Desactivado)"
            elif modelo_precio in ["Pesado", "Pulsera Combo", "Con Piedra", "Piercing", "Fabricación"]:
                lbl_crea = "Creativo *"
            else:
                lbl_crea = "Creativo (Opcional)"
            
            creativo = st.text_input(lbl_crea, key="in_creativo", disabled=es_set)
            
            if lbl_crea == "Creativo *" and not creativo: 
                errores_validacion.append("Creativo")

            lbl_ubi = "Ubicación *" if modelo_precio in ["Pesado", "Oferta", "Pulsera Combo", "Con Piedra", "Piercing"] else "Ubicación (Opcional)"
            ubicacion = st.selectbox(lbl_ubi, opc_ubicacion, key="in_ubicacion")
            if lbl_ubi == "Ubicación *" and ubicacion == "Seleccione...": errores_validacion.append("Ubicación")
            
        with c_gen3:
            coleccion = st.selectbox("Colección (Opcional)", opc_coleccion, key="in_coleccion")
            
        adicional = st.text_input("Adicional (Colores-Formas) (Opcional)", key="in_adicional")

        if ubicacion == "Bodega 429 Medellin":
            st.divider()
            st.subheader("Nomenclatura de Ubicación (Bodega)")
            letras_az = [chr(i) for i in range(65, 91)]
            c_ubi1, c_ubi2, c_ubi3 = st.columns(3)
            
            with c_ubi1:
                st.write("Columna (A-Z) (Opcional)")
                btn_texto_col = st.session_state.pop_col if st.session_state.pop_col else "Seleccionar"
                with st.popover(btn_texto_col, use_container_width=True):
                    grid_cols = st.columns(5)
                    for i, letra in enumerate(letras_az):
                        if grid_cols[i % 5].button(letra, key=f"btn_c_{letra}", use_container_width=True):
                            st.session_state.pop_col = letra
                            st.rerun() 
            with c_ubi2:
                st.write("Paño (1-50) (Opcional)")
                btn_texto_pano = str(st.session_state.pop_pano) if st.session_state.pop_pano else "Seleccionar"
                with st.popover(btn_texto_pano, use_container_width=True):
                    grid_panos = st.columns(5)
                    for num in range(1, 51):
                        if grid_panos[(num - 1) % 5].button(str(num), key=f"btn_p_{num}", use_container_width=True):
                            st.session_state.pop_pano = num
                            st.rerun()
            with c_ubi3:
                st.write("Celda (A-Z) (Opcional)")
                btn_texto_celda = st.session_state.pop_celda if st.session_state.pop_celda else "Seleccionar"
                with st.popover(btn_texto_celda, use_container_width=True):
                    grid_celdas = st.columns(5)
                    for i, letra in enumerate(letras_az):
                        if grid_celdas[i % 5].button(letra, key=f"btn_ce_{letra}", use_container_width=True):
                            st.session_state.pop_celda = letra
                            st.rerun()
        else:
            st.session_state.pop_col = ""
            st.session_state.pop_pano = ""
            st.session_state.pop_celda = ""

        st.divider()

        bloquear_boton = len(errores_validacion) > 0
        if bloquear_boton:
            st.error(f"Faltan datos obligatorios para este modelo/categoría: {', '.join(errores_validacion)}")
            
        if st.button("Guardar Registro", type="primary", disabled=bloquear_boton, use_container_width=True):
            
            val_creativo = st.session_state.get('in_creativo', "")
            val_talla = st.session_state.get('in_talla', "")
            val_set1 = st.session_state.get('in_set1', "")
            val_set2 = st.session_state.get('in_set2', "")
            val_adic = st.session_state.get('in_adicional', "")
            val_ubi = st.session_state.get('in_ubicacion', "Seleccione...")
            val_broche = st.session_state.get('in_broche', "Seleccione...")
            val_genero = st.session_state.get('in_genero', "Seleccione...")
            val_coleccion = st.session_state.get('in_coleccion', "Ninguna")
            
            val_piedra = st.session_state.get('in_piedra', [])
            
            val_rec1 = st.session_state.get('in_rec1', "Seleccione...")
            val_rec2 = st.session_state.get('in_rec2', "Seleccione...")
            
            # --- FORMATEO FINAL ---
            creativo_upper = val_creativo.upper() if val_creativo and not es_set else ""
            talla_anillo_upper = val_talla.upper() if val_talla else ""
            set_c_1_upper = val_set1.upper() if val_set1 else ""
            set_c_2_upper = val_set2.upper() if val_set2 else ""
            adicional_upper = val_adic.upper() if val_adic else ""
            ubicacion_final = val_ubi if val_ubi != "Seleccione..." else ""
            broche_final = val_broche if val_broche != "Seleccione..." else ""
            genero_final = val_genero if val_genero != "Seleccione..." else ""
            
            peso_fmt = formato_decimal_sheets(st.session_state.get('in_peso', 0.0))
            peso_2_fmt = formato_decimal_sheets(st.session_state.get('in_peso2', 0.0))
            cm_oblig_fmt = formato_decimal_sheets(st.session_state.get('in_cm_ob', 0.0))
            cm_opc_fmt = formato_decimal_sheets(st.session_state.get('in_cm_op', 0.0))
            grosor_mm_fmt = formato_decimal_sheets(st.session_state.get('in_mm', 0.0))
            set_d_cm_fmt = formato_decimal_sheets(st.session_state.get('in_setd', 0.0))
            
            recargo_1_final = "" if val_rec1 == "Seleccione..." else val_rec1
            recargo_2_final = "" if val_rec2 == "Seleccione..." else val_rec2
            
            piedra_final = ", ".join(val_piedra) if len(val_piedra) > 0 else ""
            
            coleccion_final = "" if val_coleccion == "Ninguna" else val_coleccion
            costo_manual_final = "" if st.session_state.get('in_costo', 0) == 0 else st.session_state.get('in_costo', 0)
            
            # --- SOLUCIÓN DEL DESCUENTO CON SÍMBOLO % ---
            # Al concatenar el símbolo %, Sheets activa su propio reconocimiento de porcentajes 
            # y transforma "7%" en el valor real 0.07 conservando el diseño visual de "7,00%".
            val_desc = st.session_state.get('in_desc', 0)
            descuento_final = f"{val_desc}%" if val_desc > 0 else ""

            # DICCIONARIO 1: Hoja "Inputs"
            datos_a_guardar = {
                "A": material,
                "B": modelo_precio,
                "C": qts_ley,
                "D": categoria,
                "E": peso_fmt,
                "F": recargo_1_final,
                "G": peso_2_fmt,
                "H": recargo_2_final,
                "I": costo_manual_final,
                "J": piedra_final,
                "K": descuento_final,
                "N": creativo_upper,
                "O": color_oro,
                "P": cm_oblig_fmt,
                "Q": cm_opc_fmt,
                "R": grosor_mm_fmt,
                "S": talla_anillo_upper,
                "T": set_c_1_upper,
                "U": set_c_2_upper,
                "V": set_d_cm_fmt,
                "W": adicional_upper,
                "Y": broche_final,
                "Z": coleccion_final,
                "AC": genero_final,
                "AD": ubicacion_final
            }
            
            # DICCIONARIO 2: Hoja "Ubicación"
            datos_ubicacion_guardar = None
            if val_ubi == "Bodega 429 Medellin":
                datos_ubicacion_guardar = {
                    "C": st.session_state.pop_col,
                    "D": st.session_state.pop_pano,
                    "E": st.session_state.pop_celda
                }
            
            with st.spinner('Enviando datos a la nube...'):
                mi_archivo_id = st.session_state.get('sheet_asignado')
                exito = agregar_registro(datos_a_guardar, datos_ubicacion_guardar, mi_archivo_id)
                
            if exito:
                st.success(f"Registro exitoso! (Auxiliar: {auxiliar_actual})")
                st.session_state.hoja_limpia = False 
                st.button("Registrar Nuevo Artículo", type="secondary", on_click=limpiar_formulario_parcial)
            else:
                st.error("Hubo un problema de conexión. Revisa tu terminal.")
    else:
        st.info("Selecciona Material, Modelo y Categoría para comenzar la cotización.")

    st.divider()
    st.subheader("Zona de Administración")
    
    with st.expander("Limpiar todos los registros de la Hoja de Cálculo"):
        if st.session_state.hoja_limpia:
            st.info("La hoja ya se encuentra limpia. Agrega un nuevo registro para habilitar esta opción.")
        else:
            st.warning("ATENCIÓN: Esta acción vaciará todos los datos ingresados previamente. Las fórmulas y listas quedarán intactas.")
            confirmacion = st.checkbox("Entiendo que esta acción es irreversible y deseo borrar todos los registros.")
            
            if st.button("Limpiar Hojas de Cálculo", type="primary", disabled=not confirmacion):
                with st.spinner("Eliminando datos de Sheets..."):
                    mi_archivo_id = st.session_state.get('sheet_asignado')
                    exito_limpieza = limpiar_registros(mi_archivo_id)
                    
                    if exito_limpieza == "VACIO":
                        st.info("La hoja de cálculo ya estaba vacía (Solo contiene títulos). No se realizaron cambios.")
                        st.session_state.hoja_limpia = True
                        st.rerun()
                    elif exito_limpieza == True:
                        st.success("La hoja ha sido limpiada con éxito.")
                        st.session_state.hoja_limpia = True 
                        st.rerun() 
                    else:
                        st.error("Ocurrió un error intentando limpiar la hoja. Revisa tu terminal.")