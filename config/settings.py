import os
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'credenciales.json')

# El ID extraído del enlace que me acabas de dar:
MASTER_SPREADSHEET_ID = os.getenv("MASTER_SPREADSHEET_ID", "1WY_oSWf5QNHdSe1--MPamMUrrHwZ6kYYPHwV06qKkNk")

WORKSHEET_NAME = "Inputs"

# URL del webhook n8n — configurar en .env después de activar el flujo
WEBHOOK_N8N_URL = os.getenv("WEBHOOK_N8N_URL", "")