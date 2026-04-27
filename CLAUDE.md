# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (starts on http://localhost:8501)
streamlit run main.py

# Install dependencies
pip install -r requirements.txt
```

No build, lint, or test infrastructure exists — this is a pure Streamlit app with manual testing only.

## Architecture

Streamlit web app for jewelry inventory registration into Google Sheets. The language of the UI and all field names is Spanish.

**Session state routing in `main.py`:**
- Unauthenticated → `ui/login_view.py`
- Authenticated → `ui/form_view.py`
- Security lockout: 3 failed logins trigger a 60-second block tracked in session state (`intentos_fallidos`, `bloqueado_hasta`)

**Authentication (`services/auth.py`):**
- Connects to a master Google Sheet ("Control_de_Accesos") to validate credentials
- Returns the user's name and their **assigned spreadsheet ID** on success
- User must have status "ACTIVO" in the master sheet

**Form (`ui/form_view.py`):**
- The largest and most complex file — ~21KB of conditional rendering logic
- Fields are conditionally shown/required based on three main selectors:
  - **Material** (Oro/Plata) → determines available Ley values and colors
  - **Categoria** → determines which dimension fields appear (from `config/form_rules.json`)
  - **Modelo de Precio** (Pesado, Oferta, Con Piedra, etc.) → determines required pricing fields
- Special case: selecting "Bodega 429 Medellin" as location shows a grid popover for Column/Row/Cell storage coordinates
- On submit, calls `agregar_registro()` with two dicts:
  - `datos_inputs` → columns A–AD of the "Inputs" sheet
  - `datos_ubicacion` → columns C–E of the "Ubicación" sheet

**Google Sheets integration (`services/google_sheets.py`):**
- `conectar_documento(sheet_id)` — authenticates with service account and opens the spreadsheet
- `agregar_registro(datos_inputs, datos_ubicacion, sheet_id)` — finds next empty row in col A and writes data across both sheets via `batch_update`
- `limpiar_registros(sheet_id)` — bulk-clears specific column ranges (aborts if sheet is already empty)
- Decimal separator: converts `.` → `,` before writing, since Google Sheets in Spanish locale uses commas

**Configuration:**
- `config/settings.py` — credentials path, master spreadsheet ID, worksheet name ("Inputs")
- `config/form_rules.json` — all dropdown option lists and the conditional field logic (category → mandatory/optional field mappings)
- `credentials/credenciales.json` — Google service account key, `.gitignored`, must be provided manually

## Google Sheets Data Model

Each user has their own assigned spreadsheet (ID stored in the master sheet). That spreadsheet has two worksheets:
- **Inputs** — main inventory data (columns A–AD)
- **Ubicación** — storage location data (columns C–E)

The master spreadsheet ("Control_de_Accesos") maps usernames/passwords to their assigned sheet IDs and ACTIVO/INACTIVO status.
