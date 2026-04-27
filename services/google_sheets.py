import gspread
from google.oauth2.service_account import Credentials
from config.settings import CREDENTIALS_PATH, WORKSHEET_NAME

# Columnas de datos gestionadas por el programa (letra → índice 0-based)
_DATA_COLS = {
    'A': 0,  'B': 1,  'C': 2,  'D': 3,  'E': 4,  'F': 5,  'G': 6,  'H': 7,
    'I': 8,  'J': 9,  'K': 10, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
    'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'Y': 24, 'Z': 25,
    'AA': 26, 'AC': 28, 'AD': 29
}

def conectar_documento(sheet_id):
    """Establece la conexión al documento dinámico del auxiliar logueado."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        credenciales = Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=scopes
        )
        cliente = gspread.authorize(credenciales)
        # Se conecta exclusivamente al archivo del auxiliar
        return cliente.open_by_key(sheet_id)
    except Exception as e:
        print(f"Error crítico al conectar: {e}")
        return None

def agregar_registro(datos_inputs, datos_ubicacion, sheet_id):
    """
    Guarda los datos en el Sheets asignado al usuario.
    """
    doc = conectar_documento(sheet_id)
    if not doc:
        return False
        
    try:
        pestaña_inputs = doc.worksheet(WORKSHEET_NAME)
        pestaña_ubicacion = doc.worksheet("Ubicación")
        
        # 1. Encontrar la siguiente fila vacía buscando en la Columna A
        columna_a = pestaña_inputs.col_values(1)
        siguiente_fila = len(columna_a) + 1
        
        # 2. Formatear y enviar datos a 'Inputs'
        batch_inputs = []
        for col, val in datos_inputs.items():
            batch_inputs.append({
                'range': f"{col}{siguiente_fila}",
                'values': [[val]]
            })
        pestaña_inputs.batch_update(batch_inputs, value_input_option="USER_ENTERED")
        
        # 3. Formatear y enviar datos a 'Ubicación' (si aplica)
        if datos_ubicacion:
            batch_ubi = []
            for col, val in datos_ubicacion.items():
                batch_ubi.append({
                    'range': f"{col}{siguiente_fila}",
                    'values': [[val]]
                })
            pestaña_ubicacion.batch_update(batch_ubi, value_input_option="USER_ENTERED")
            
        return True
    except Exception as e:
        print(f"Error al insertar datos: {e}")
        return False

def limpiar_registros(sheet_id):
    """
    Vacía las celdas del Sheets asignado al usuario.
    """
    doc = conectar_documento(sheet_id)
    if not doc:
        return False
        
    try:
        pestaña_inputs = doc.worksheet(WORKSHEET_NAME)
        
        # --- BLOQUEO DE SEGURIDAD BACKEND ---
        columna_a = pestaña_inputs.col_values(1)
        if len(columna_a) <= 1:
            return "VACIO" # Abortamos antes de tocar el Sheets
            
        pestaña_ubicacion = doc.worksheet("Ubicación")
        
        # Limpiamos Inputs por rangos específicos (Se añadió AA2:AB3000)
        rangos_inputs = ["A2:K3000", "N2:W3000", "Y2:Z3000", "AA2:AB3000", "AC2:AD3000"]
        pestaña_inputs.batch_clear(rangos_inputs)
        
        # Limpiamos Ubicación
        rangos_ubicacion = ["C2:E3000"]
        pestaña_ubicacion.batch_clear(rangos_ubicacion)
        
        return True
    except Exception as e:
        print(f"Error al limpiar datos: {e}")
        return False

def obtener_ultimos_registros(sheet_id, n=5):
    doc = conectar_documento(sheet_id)
    if not doc:
        return None
    try:
        hoja = doc.worksheet(WORKSHEET_NAME)
        todos = hoja.get_all_values()
        if len(todos) <= 1:
            return []
        # Solo filas donde col A (Material) tiene dato real, ignorando filas de fórmulas vacías
        filas_con_datos = [
            {"fila": i + 2, "datos": fila}
            for i, fila in enumerate(todos[1:])
            if fila and fila[0].strip()
        ]
        return filas_con_datos[-n:]
    except Exception as e:
        print(f"Error obteniendo últimos registros: {e}")
        return None

def eliminar_fila(sheet_id, fila_numero):
    doc = conectar_documento(sheet_id)
    if not doc:
        return False
    try:
        hoja_inputs = doc.worksheet(WORKSHEET_NAME)
        hoja_ubi    = doc.worksheet("Ubicación")

        todos_inputs = hoja_inputs.get_all_values()
        todos_ubi    = hoja_ubi.get_all_values()

        # Filas con dato real en col A, con su número de fila original
        filas_orig = [
            (i + 2, fila)
            for i, fila in enumerate(todos_inputs[1:])
            if str(fila[0]).strip()
        ]
        if not filas_orig:
            return True

        ultima_fila = filas_orig[-1][0]

        # Lookup ubicación por número de fila original
        ubi_por_fila = {}
        for i, fila in enumerate(todos_ubi[1:]):
            row = i + 2
            c = fila[2] if len(fila) > 2 else ""
            d = fila[3] if len(fila) > 3 else ""
            e = fila[4] if len(fila) > 4 else ""
            if c or d or e:
                ubi_por_fila[row] = (c, d, e)

        # Filas a conservar (excluir la eliminada)
        filas_mantener     = [(r, f) for r, f in filas_orig if r != fila_numero]
        ubi_mantener       = [ubi_por_fila.get(r, ("", "", "")) for r, _ in filas_orig if r != fila_numero]

        # Limpiar rango completo de datos (columnas gestionadas)
        hoja_inputs.batch_clear([
            f"A2:K{ultima_fila}", f"N2:W{ultima_fila}",
            f"Y2:Z{ultima_fila}", f"AA2:AB{ultima_fila}", f"AC2:AD{ultima_fila}"
        ])
        hoja_ubi.batch_clear([f"C2:E{ultima_fila}"])

        # Reescribir datos desplazados hacia arriba
        if filas_mantener:
            batch_in = [
                {'range': f'{col}{new_row}', 'values': [[fila[idx] if idx < len(fila) else ""]]}
                for new_row, (_, fila) in enumerate(filas_mantener, start=2)
                for col, idx in _DATA_COLS.items()
            ]
            hoja_inputs.batch_update(batch_in, value_input_option="USER_ENTERED")

            batch_ubi = [
                {'range': f'{col}{new_row}', 'values': [[val]]}
                for new_row, (c, d, e) in enumerate(ubi_mantener, start=2)
                for col, val in [('C', c), ('D', d), ('E', e)]
                if val
            ]
            if batch_ubi:
                hoja_ubi.batch_update(batch_ubi, value_input_option="USER_ENTERED")

        print(f"[OK] Fila {fila_numero} eliminada. {len(filas_mantener)} registros restantes.")
        return True
    except Exception as e:
        print(f"[ERROR] eliminar_fila({fila_numero}): {e}")
        return False

def actualizar_fila(sheet_id, fila_numero, datos_inputs, datos_ubicacion):
    doc = conectar_documento(sheet_id)
    if not doc:
        return False
    try:
        hoja_inputs = doc.worksheet(WORKSHEET_NAME)
        batch_inputs = [
            {'range': f"{col}{fila_numero}", 'values': [[val]]}
            for col, val in datos_inputs.items()
        ]
        hoja_inputs.batch_update(batch_inputs, value_input_option="USER_ENTERED")

        hoja_ubi = doc.worksheet("Ubicación")
        if datos_ubicacion:
            batch_ubi = [
                {'range': f"{col}{fila_numero}", 'values': [[val]]}
                for col, val in datos_ubicacion.items()
            ]
            hoja_ubi.batch_update(batch_ubi, value_input_option="USER_ENTERED")
        else:
            hoja_ubi.batch_clear([f"C{fila_numero}:E{fila_numero}"])

        return True
    except Exception as e:
        print(f"Error actualizando fila {fila_numero}: {e}")
        return False

def obtener_effiload(sheet_id):
    doc = conectar_documento(sheet_id)
    if not doc:
        return None
    try:
        hoja = doc.worksheet("EFFILoad")
        todos = hoja.get_all_values()
        if not todos:
            return []
        encabezados = todos[0]
        filas_datos = []
        for fila in todos[1:]:
            col_a = str(fila[0]).strip() if fila else ""
            if not col_a or col_a.startswith('#'):
                break  # Fila de fórmula sin dato o con error → detener
            filas_datos.append(fila)
        return [encabezados] + filas_datos
    except Exception as e:
        print(f"Error obteniendo EFFILoad: {e}")
        return None