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
        
        # Limpiamos Inputs por rangos específicos
        rangos_inputs = ["A2:K3000", "N2:W3000", "Y2:Z3000", "AC2:AD3000"]
        pestaña_inputs.batch_clear(rangos_inputs)
        
        # Limpiamos Ubicación
        rangos_ubicacion = ["C2:E3000"]
        pestaña_ubicacion.batch_clear(rangos_ubicacion)
        
        return True
    except Exception as e:
        print(f"Error al limpiar datos: {e}")
        return False