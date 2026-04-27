import gspread
from google.oauth2.service_account import Credentials
from config.settings import CREDENTIALS_PATH, WORKSHEET_NAME

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
        doc.worksheet(WORKSHEET_NAME).delete_rows(fila_numero)
        doc.worksheet("Ubicación").delete_rows(fila_numero)
        return True
    except Exception as e:
        print(f"Error eliminando fila {fila_numero}: {e}")
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