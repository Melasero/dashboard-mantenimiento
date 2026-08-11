"""
Descarga desde Google Drive (Shared Drive "InformacionStracon") los insumos
que Dashboard_Ejecutivo_Mantenimiento_v6.py necesita, usando una cuenta de
servicio (sin interacción humana) -- pensado para correr dentro de un runner
de GitHub Actions, donde no existe un G:/ montado ni un usuario que haga
drive.mount().

Requiere la variable de entorno GDRIVE_SA_KEY_JSON con el JSON completo de
la cuenta de servicio (se inyecta desde el secreto de GitHub Actions del
mismo nombre). Esa cuenta de servicio debe estar agregada como miembro
(alcanza con "Lector") de la Unidad Compartida "InformacionStracon".
"""
import io
import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# ID de la carpeta ".../ALMACEN STRACON/MANTENIMIENTO STRACON/REPORTE SUPERVISOR"
# en el Shared Drive "InformacionStracon" (estable; no es un dato sensible: el
# acceso real lo controla el permiso de la cuenta de servicio, no el ID).
CARPETA_REPORTE_SUPERVISOR_ID = "1AdV2NSDENZ23Xg-0Xgfg33UkKqRCfwrX"

ARCHIVOS_RAIZ_A_DESCARGAR = [
    "Sistema_Control_Mantenimiento_Diario (1).xlsm",
    "motor_d13c.png",
]


def _cliente_drive():
    info = json.loads(os.environ["GDRIVE_SA_KEY_JSON"])
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _listar_hijos(servicio, carpeta_id):
    archivos, page_token = [], None
    while True:
        resp = servicio.files().list(
            q=f"'{carpeta_id}' in parents and trashed = false",
            corpora="allDrives",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
        ).execute()
        archivos.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            return archivos


def _descargar_archivo(servicio, file_id, destino):
    request = servicio.files().get_media(fileId=file_id, supportsAllDrives=True)
    os.makedirs(os.path.dirname(destino) or ".", exist_ok=True)
    with io.FileIO(destino, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    print(f"  ✓ {destino}")


def main():
    servicio = _cliente_drive()
    hijos = _listar_hijos(servicio, CARPETA_REPORTE_SUPERVISOR_ID)
    por_nombre = {h["name"]: h for h in hijos}

    print("📥 Descargando insumos desde Drive (REPORTE SUPERVISOR)...")
    faltantes = []
    for nombre in ARCHIVOS_RAIZ_A_DESCARGAR:
        item = por_nombre.get(nombre)
        if not item:
            faltantes.append(nombre)
            continue
        _descargar_archivo(servicio, item["id"], nombre)

    if faltantes:
        print(f"  ⚠️  No se encontraron en Drive: {faltantes}")
        if "Sistema_Control_Mantenimiento_Diario (1).xlsm" in faltantes:
            print("❌ Sin el Excel principal no se puede generar el dashboard.")
            sys.exit(1)

    print("✅ Insumos listos.")


if __name__ == "__main__":
    main()
