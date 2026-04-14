import gspread
from google.oauth2.service_account import Credentials
from config.settings import CREDENTIALS_PATH, MASTER_SPREADSHEET_ID

def conectar_maestro():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credenciales = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        return cliente.open_by_key(MASTER_SPREADSHEET_ID).worksheet("Control_de_Accesos")
    except Exception as e:
        print(f"Error al conectar con el Maestro: {e}")
        return None

def autenticar_usuario(usuario_input, password_input):
    hoja_maestra = conectar_maestro()
    if not hoja_maestra:
        return False, "Error de conexión con el servidor.", None

    usr_in = str(usuario_input).strip()
    pwd_in = str(password_input).strip()

    try:
        filas = hoja_maestra.get_all_values()
        if len(filas) <= 1:
            return False, "No hay usuarios registrados en el sistema.", None

        print("\n--- INICIANDO VALIDACIÓN DE USUARIOS ---")

        for i, fila in enumerate(filas[1:], start=2):
            partes = []

            for celda in fila:
                celda_str = str(celda).strip()
                if celda_str:
                    celda_str = celda_str.replace('[', '').replace(']', '').replace("'", "")
                    if ',' in celda_str:
                        partes.extend([x.strip() for x in celda_str.split(',') if x.strip()])
                    else:
                        partes.append(celda_str)

            if len(partes) >= 5:
                user_db    = str(partes[0])          # ✅ índice 0
                pass_db    = str(partes[1])          # ✅ índice 1
                nombre_aux = str(partes[2])          # ✅ índice 2
                sheet_id   = str(partes[3])          # ✅ índice 3
                estado     = str(partes[4]).upper()  # ✅ índice 4

                print(f"Fila {i} | BD User: '{user_db}' | BD Pass: '{pass_db}' | Estado: '{estado}'")

                if user_db == usr_in and pass_db == pwd_in:
                    print("  -> ¡COINCIDENCIA EXACTA!")
                    if estado != 'ACTIVO':
                        print(f"  [X] Acceso denegado: Usuario {nombre_aux} inactivo.")
                        return False, "Usuario inactivo. Contacte al administrador.", None

                    print(f"  [✓] Ingresando al archivo de {nombre_aux}...")
                    return True, nombre_aux, sheet_id

        print("--- FIN DE VALIDACIÓN (RECHAZADO) ---\n")
        return False, "Usuario o contraseña incorrectos.", None

    except Exception as e:
        print(f"Error leyendo usuarios: {e}")
        return False, "Error interno validando credenciales.", None