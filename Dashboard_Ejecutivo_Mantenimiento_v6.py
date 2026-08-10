"""
================================================================================
 SISTEMA DE CONFIABILIDAD Y GENERADOR DE DASHBOARD EJECUTIVO INTERACTIVO
 v2.0 — "Clase Mundial" Edition
 Cliente: STRACON - Operación Antamina | Flota: Volvo FMX 8x4 R — Motor D13C (540 HP)
 Autor: Vince Rivera (Fleet Reliability / Full-Stack Data Viz)
================================================================================

Mejoras clave respecto a v1:
 - Robustez: validación de columnas/hojas con mensajes claros, sin crashear
   silenciosamente en producción.
 - UI/UX Premium: Dark Mode "Glassmorphism", paleta minera (azul profundo,
   naranja/ámbar tipo CAT, verde esmeralda, rojo carmesí), micro-animaciones.
 - Gráficos enriquecidos: hover unificado, curva Pareto 80/20 acumulada,
   matriz de criticidad MTBF vs MTTR (bubble chart), sin márgenes invasivos.
 - Filtros cruzados en JS: al filtrar por grupo/equipo/semana/fechas, los
   KPIs superiores (DM Global, MTBF, MTTR, Fallas) se RECALCULAN en vivo,
   no solo la tabla.
 - Exportación a CSV de la tabla filtrada, 100% client-side.
 - Resaltado visual de "Top Offenders" (equipos que más disponibilidad
   consumen) y de equipos fuera de meta contractual.
 - Un único archivo HTML autocontenido (CSS+JS embebido, sin backend).

v3.0 — Metodología de cálculo blindada + pulido visual "premium":
 - Algoritmo de fusión de intervalos (interval merging) para Horas Inoperativas
   acotado al rango de fechas seleccionado, exactamente como especifica la
   metodología oficial: %DM = max(0, min(100, (HorasPeriodo - InopExactas) /
   HorasPeriodo * 100)); MTBF = HorasOperativas / Fallas; MTTR = InopExactas / Fallas.
   NOTA DE INGENIERÍA: la especificación entregada tenía una errata en la línea
   `finAcotado = fFinInterv < dFinFiltro ? fFinInterv : dInicioFiltro` (el rama
   "else" debía ser `dFinFiltro`, no `dInicioFiltro`); de mantenerse tal cual,
   cualquier intervención que siga abierta más allá del fin del periodo
   filtrado colapsaría a una duración negativa/nula, subestimando el tiempo
   inoperativo real. Aquí se implementa la versión corregida
   (`... : dFinFiltro`), que es la única consistente con la fórmula de %DM.
 - KPIs Globales de Flota (Python): DM_global = ΣTPF / (ΣTPF + ΣTPR) * 100;
   MTBF_global = ΣTPF / ΣFallas; MTTR_global = ΣTPR / ΣFallas.
 - Preparación de datos: H_INICIO_REAL = H.PARADA.fillna(H.INICIO INTERV.);
   duración neta = (H.FIN INTERV. - H_INICIO_REAL) con H_NETAS_REPARACION
   como fallback; solo se consideran intervenciones con APLICA DM == 'SI'.
 - Cumplimiento PM = (tareas con HRS EJECUTADAS > 0) / (tareas programadas) * 100.
 - Glow borders premium en cards KPI, badges con pulso animado para
   "Top Offenders", brechas negativas resaltadas en rojo brillante, y
   hover templates enriquecidos (meta, brecha, estado, promedio h/evento).

v4.0 — "Executive Industrial UI": Gauge de DM, Donut de inoperatividad,
   trendline semanal de PM, tabla con buscador/orden/pastillas/progress-bar,
   corrección de visibilidad de la columna EQUIPO, cuadrantes anotados en
   la matriz de criticidad.

v5.0 — "Cyber-Executive Dark": paleta Deep Navy (#0b0f19) / panel (#151c2c)
   con acentos neón (cian, magenta), KPIs gigantes con micro-indicadores de
   tendencia (DM vs meta contractual, MTBF/MTTR vs mediana de flota), y
   recoloreo neón contrastante en los gráficos de PM y Otras Actividades.
   La matemática de KPIs/DM permanece sin cambios en todas las versiones.

v6.0 — "Ultra-Executive Suite":
 - Mini-toolbar independiente por gráfico: Top N (5/10/Criticidad/Todos) en el
   gráfico de DM y en el Pareto; selector de métrica local en el Pareto
   (Horas Parada / N° Eventos / MTTR) sin recargar la página; botón de
   Enfoque/Fullscreen ("modo cine" translúcido) en cada tarjeta de gráfico.
   Para lograrlo, los gráficos de DM y Pareto pasaron de figuras Plotly
   estáticas (generadas en Python) a trazas Plotly.js construidas en el
   navegador con Plotly.react() sobre datasets JSON serializados desde Python.
 - Cross-filtering bidireccional: clic en una barra del Pareto filtra tabla y
   KPIs por ese SISTEMA (el universo de intervenciones se restringe; la
   fórmula %DM/fusión de intervalos NO cambia); clic en un equipo (gráfico DM
   o badge de la tabla) activa el filtro global por equipo. Chip flotante
   inferior "Filtrando por: ... (clic para limpiar)".
 - Gauge rediseñado: anillo neón ultrafino (color según estado: verde/cian/
   rojo) sobre track neutro translúcido, sin bloques macizos de color.
 - Corrección definitiva de visibilidad de la columna EQUIPO: badge
   `.badge-equipo` con fondo forzado #151c2c, texto #f8fafc y borde neón.
 - LED pulse badges (verde titilante si cumple, rojo si crítico) en la tabla.
 - Tooltips premium en todos los gráficos: fondo translúcido, borde iluminado
   cian, tipografía monoespaciada (JetBrains Mono) y desglose de Brecha pp,
   Meta y Días sin fallas (gráfico DM).
 - Sparklines SVG inline en las tarjetas KPI: tendencia semanal aproximada de
   %DM de flota y de N° de fallas (ver nota metodológica en
   `calcular_tendencia_semanal_flota`: es un indicador ilustrativo por semana
   calendario completa; no reemplaza el %DM oficial del rango filtrado).

v7.0 — "Real Data + Ficha Técnica FMX":
 - BUG FIX Tipo de Flota: la clasificación CONTRATO/CLIENTE/ALQUILADOS ahora se
   deriva de la columna real "Contrato_Gold" de PARQUE DE EQUIPOS (limpiada con
   strip/upper, unidades DESMOVILIZADO excluidas de la flota activa), en vez de
   comparar la columna GRUPO de la hoja KPIs (tipo de equipo, no de contrato)
   contra el literal "FLOTA FMX", que nunca calzaba y dejaba el filtro "Cliente"
   siempre en 0 (ver `clasificar_categoria_flota`).
 - Velocímetro DM Global: mini-toolbar con filtros combinables de Semana, Tipo de
   Flota y Rango de Fechas. Fuera del estado por defecto (sin filtros), el %DM/meta
   se recalcula 100% en vivo en JS reutilizando la MISMA fórmula oficial de fusión
   de intervalos (`calcularHorasInopExactas`) sobre el universo completo de
   equipos del parque, no solo los de la hoja KPIs — así el filtro nunca queda
   "pegado en 0" para equipos sin registro oficial consolidado.
 - Sección de Ficha Técnica Volvo FMX — Motor D13C (540 HP): banner ilustrativo
   (SVG inline) con los componentes clave del volquete (motor, freno de motor
   VEB+, transmisión I-Shift HD, ejes de reducción de cubo, tolva Hardox), estilo
   Cyber-Industrial (#0d1117 / #00b4d8 / #ffd166). Puramente informativo: no
   participa en ningún cálculo del dashboard.
"""

import sys
import warnings
import webbrowser
import re
import calendar
from pathlib import Path
import json
import base64

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

warnings.filterwarnings("ignore")

# Los prints de progreso usan emojis (🚀📊✅⚠️...). La consola de Windows suele
# usar cp1252 por defecto, que no puede codificarlos y hace crashear el script
# (o el .exe compilado con --windowed, donde el error queda totalmente oculto).
# Se fuerza UTF-8 en stdout/stderr cuando existen; en modo --windowed puro
# sys.stdout puede ser None, por eso el guard.
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# ==============================================================================
# 0. CONFIGURACIÓN GENERAL
# ==============================================================================
# Rutas relativas al directorio de trabajo del script (deliberado: así funciona
# igual en Windows ejecutándolo directo desde la carpeta "REPORTE SUPERVISOR" del
# Shared Drive (letra G: mapeada) que en Google Colab, tras
# `os.chdir(".../REPORTE SUPERVISOR")` sobre el Drive montado — sin rutas
# absolutas "G:\..." hardcodeadas que solo existen en una máquina.
ARCHIVO_ENTRADA = "Sistema_Control_Mantenimiento_Diario (1).xlsm"
ARCHIVO_SALIDA_HTML = "Dashboard_Ejecutivo_Mantenimiento.html"
RUTA_IMAGEN_MOTOR_D13C = "motor_d13c.png"

# Archivos de horómetros (reportes "Rendimiento" de Volvo Connect) — usados EXCLUSIVAMENTE
# por el módulo independiente de MTBS (ver sección D al final del archivo).
RUTA_HOROMETROS_MAYO = r"C:\Users\Admin\Downloads\horometros\mayo.xlsx"
RUTA_HOROMETROS_JUNIO = r"C:\Users\Admin\Downloads\horometros\straconSa-performance-20260723 (1).xlsx"
RUTA_HOROMETROS_JULIO = r"C:\Users\Admin\Downloads\horometros\straconSa-performance-20260723.xlsx"

# Carpeta dinámica de reportes Volvo Connect (ETL de hábitos operativos: Ralentí,
# PTO, Punto muerto, Programador de velocidad, Consumo). Cuenta Volvo Connect
# multi-sitio: cada Excel trae vehículos de VARIAS operaciones/clientes, no solo
# STRACON-Antamina — de ahí el INNER JOIN estricto contra la flota Volvo FMX en
# `construir_fact_volvo_connect`. Usada EXCLUSIVAMENTE por el módulo MTBS.
RUTA_CARPETA_VOLVO_CONNECT = "REPORTE DE VOLVO CONNECT"

MESES_ES = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "SETIEMBRE": 9, "OCTUBRE": 10,
    "NOVIEMBRE": 11, "DICIEMBRE": 12,
}

SHEET_PARQUE = "PARQUE DE EQUIPOS"
SHEET_INTERVENCIONES = "Registro de Intervenciones"
SHEET_PM_PLAN = "BD_Mantenimiento"
SHEET_KPIS = "KPIs"
SHEET_SOS = "SOS"
SHEET_DETALLE_BKL = "DETALLE_BKL"

# Paleta de colores "Cyber-Executive Dark" — SaaS industrial premium
COLOR_BG_DEEP = "#0b0f19"         # Deep Navy
COLOR_PANEL = "#151c2c"           # Panel base
COLOR_ACCENT_ORANGE = "#f7931e"   # Ámbar/Naranja tipo CAT
COLOR_ACCENT_BLUE = "#38bdf8"     # Azul técnico / cian
COLOR_OK = "#10b981"              # Verde esmeralda — cumplimiento
COLOR_CRITICAL = "#dc2626"        # Rojo carmesí — fallas/crítico
COLOR_WARNING = "#f59e0b"         # Ámbar advertencia
COLOR_MUTED = "#64748b"
COLOR_VIOLET = "#a78bfa"          # Violeta neón — categoría CONTRATO
COLOR_CYAN = "#22d3ee"            # Cian — categoría CLIENTE
COLOR_MAGENTA = "#ec4899"         # Magenta neón — acentos de gráficos PM

# Total de equipos de la flota para el panel "Estado de Flota del Día" (Sección F,
# junto al Velocímetro DM). Requerimiento de negocio: cifra fija, no derivada del
# conteo de "PARQUE DE EQUIPOS" (que puede variar por altas/bajas/desmovilizados).
TOTAL_FLOTA_EQUIPOS = 57


# ==============================================================================
# UTILIDADES DE ROBUSTEZ
# ==============================================================================

class ErrorDatosFlota(Exception):
    """Excepción específica para errores de estructura/datos del Excel de flota."""
    pass


def verificar_columnas(df: pd.DataFrame, columnas_requeridas: list, nombre_hoja: str):
    """Valida que las columnas mínimas existan; lanza error legible en español."""
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ErrorDatosFlota(
            f"❌ La hoja '{nombre_hoja}' no contiene las columnas requeridas: {faltantes}.\n"
            f"   Columnas disponibles: {list(df.columns)}"
        )


def buscar_columna(df: pd.DataFrame, candidatos: list, nombre_hoja: str, default=None):
    """Busca la primera columna cuyo nombre contenga alguno de los tokens dados."""
    for token in candidatos:
        for c in df.columns:
            if token.upper() in str(c).upper():
                return c
    if default is not None:
        return default
    raise ErrorDatosFlota(
        f"❌ No se encontró ninguna columna en la hoja '{nombre_hoja}' que coincida con: {candidatos}."
    )


# ==============================================================================
# A. CARGA Y LIMPIEZA DE DATOS
# ==============================================================================

def cargar_parque_equipos(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, sheet_name=SHEET_PARQUE, header=3)
    except Exception as e:
        raise ErrorDatosFlota(f"❌ No se pudo leer la hoja '{SHEET_PARQUE}': {e}")

    df.columns = [str(c).strip() for c in df.columns]
    verificar_columnas(df, ["COD INTERNO"], SHEET_PARQUE)
    df = df.dropna(subset=["COD INTERNO"]).copy()
    df["COD INTERNO"] = df["COD INTERNO"].astype(str).str.strip()

    # BUG FIX — Tipo de Flota / Condición: la columna real que distingue el tipo de
    # contrato por equipo es "Contrato_Gold" (valores SI/NO/DESMOVILIZADO, con mezcla
    # de mayúsculas/minúsculas y espacios en el Excel de origen). El código anterior
    # intentaba clasificar por la columna "GRUPO" de la hoja KPIs comparándola contra
    # el literal "FLOTA FMX", valor que NUNCA aparece ahí (GRUPO en KPIs es el tipo de
    # equipo: "CAMION VOLQUETE", "CAMION CISTERNA", etc.) — por eso el filtro "Cliente"
    # quedaba siempre en 0: ese bucket solo capturaba equipos ausentes de la hoja KPIs,
    # no equipos realmente distintos por tipo de flota. Aquí se limpia y expone el dato
    # real (`clasificar_categoria_flota` lo consume más abajo).
    if "Contrato_Gold" in df.columns:
        df["Contrato_Gold"] = (
            df["Contrato_Gold"].astype(str).str.strip().str.upper()
            .replace({"NAN": "NO ESPECIFICADO", "": "NO ESPECIFICADO"})
        )
    else:
        df["Contrato_Gold"] = "NO ESPECIFICADO"

    # Excluye unidades desmovilizadas: no deben contarse como parte de la flota activa
    # en los filtros/KPIs del dashboard.
    df = df[df["Contrato_Gold"] != "DESMOVILIZADO"].copy()

    return df


def cargar_intervenciones(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, sheet_name=SHEET_INTERVENCIONES, header=1)
    except Exception as e:
        raise ErrorDatosFlota(f"❌ No se pudo leer la hoja '{SHEET_INTERVENCIONES}': {e}")

    df.columns = [str(c).strip() for c in df.columns]
    verificar_columnas(df, ["EQUIPO"], SHEET_INTERVENCIONES)
    df = df.dropna(subset=["EQUIPO"]).copy()

    # dayfirst=True: defensivo por si alguna celda viene como texto "DD/MM/YYYY" en vez
    # de un valor de fecha nativo de Excel (que pandas ya interpreta bien sin ambigüedad,
    # sin importar dayfirst). No afecta los valores que ya son datetime.
    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors="coerce")
    else:
        print(f"⚠️  Aviso: '{SHEET_INTERVENCIONES}' no tiene columna FECHA. Se usará fecha vacía.")
        df["FECHA"] = pd.NaT

    for c in ["H. PARADA", "H. INICIO INTERV.", "H. FIN INTERV."]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], dayfirst=True, errors="coerce")

    for c in ["HORÓMETRO (h)", "KILOMETRAJE (km)", "H_NETAS_REPARACION"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in ["TIPO DE INTERVENCION", "SISTEMA", "CONDICIÓN", "EQUIPO", "APLICA DM"]:
        if c in df.columns:
            df[c] = (
                df[c].astype(str).str.strip().str.upper()
                .replace({"NAN": np.nan, "": np.nan})
            )

    if "H. PARADA" in df.columns:
        df["H_INICIO_REAL"] = df["H. PARADA"].fillna(df.get("H. INICIO INTERV."))
    else:
        df["H_INICIO_REAL"] = df.get("H. INICIO INTERV.")

    if "H. FIN INTERV." in df.columns and "H_INICIO_REAL" in df.columns:
        duracion_calc = (df["H. FIN INTERV."] - df["H_INICIO_REAL"]).dt.total_seconds() / 3600
        df["Horas_Reparacion_Neta"] = df.get("H_NETAS_REPARACION", pd.Series(dtype=float)).fillna(duracion_calc)
    else:
        df["Horas_Reparacion_Neta"] = df.get("H_NETAS_REPARACION", 0)

    df["Horas_Reparacion_Neta"] = df["Horas_Reparacion_Neta"].fillna(0)
    # NOTA DE INGENIERÍA: la semana ISO por defecto de pandas (dt.isocalendar().week) queda
    # una semana adelantada respecto al calendario operativo de la operación. Se corrige
    # retrocediendo 7 días ANTES de calcular el número ISO (en vez de restarle 1 al número
    # ya calculado), para que el cambio de año se resuelva de forma nativa: p.ej. una fecha
    # en la semana ISO 1 de un año cae, al retroceder 7 días, en la semana 52/53 del año
    # anterior (según corresponda), evitando el caso inválido "semana 0".
    df["SEMANA"] = (df["FECHA"] - pd.Timedelta(days=7)).dt.isocalendar().week

    return df


def cargar_plan_pm(path: str, df_parque: pd.DataFrame = None) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, sheet_name=SHEET_PM_PLAN)
    except Exception as e:
        raise ErrorDatosFlota(f"❌ No se pudo leer la hoja '{SHEET_PM_PLAN}': {e}")

    df.columns = [str(c).strip().upper() for c in df.columns]

    col_sem = buscar_columna(df, ["SEM"], SHEET_PM_PLAN)
    # Prioriza el código de equipo (p.ej. "CODIGO SAP" -> CV-00426) sobre el chasis
    # (p.ej. "CHASIS" -> E935970): las gráficas de PM/Otras Actividades deben agrupar
    # y etiquetar por código de equipo, no por número de chasis.
    col_eq = buscar_columna(df, ["CODIGO SAP", "COD EQUIPO", "COD INTERNO", "EQUIPO", "COD", "CHASIS", "UNIDAD"], SHEET_PM_PLAN)
    col_tp = buscar_columna(df, ["TIPO", "ACTIVIDAD"], SHEET_PM_PLAN)

    col_hr_prog_candidatos = [c for c in df.columns if "PROG" in c or "PLAN" in c]
    col_hr_ejec_candidatos = [c for c in df.columns if "EJEC" in c or "REAL" in c or "DURAC" in c or "HORA" in c]

    col_hr_prog = col_hr_prog_candidatos[0] if col_hr_prog_candidatos else None
    col_hr_ejec = col_hr_ejec_candidatos[-1] if col_hr_ejec_candidatos else None

    df["SEMANA"] = pd.to_numeric(df[col_sem], errors="coerce")
    df["COD_EQUIPO"] = df[col_eq].astype(str).str.strip()

    # BUG FIX — Eje X mostraba número de chasis en vez de Código de Equipo: en el
    # Excel real la columna de código va acentuada ("CÓDIGO"), por lo que la búsqueda
    # de `col_eq` por substring sin acentos ("COD") no calza contra ella y
    # `buscar_columna` termina cayendo en el candidato de reserva "CHASIS" (p.ej.
    # "E935970" en vez de "CV-00426"). En vez de parchear solo la detección de
    # columna (frágil ante otros layouts de Excel), se cruza (JOIN) el valor de
    # COD_EQUIPO contra CHASIS -> COD INTERNO de PARQUE DE EQUIPOS (única fuente de
    # verdad del mapeo, ver `cargar_parque_equipos`) y se reemplaza por el código
    # interno correspondiente. Los valores que ya son código interno (no aparecen
    # en el mapa de chasis) quedan intactos.
    if df_parque is not None and "CHASIS" in df_parque.columns and "COD INTERNO" in df_parque.columns:
        mapa_chasis_a_cod = (
            df_parque.dropna(subset=["CHASIS", "COD INTERNO"])
            .assign(CHASIS_NORM=lambda d: d["CHASIS"].astype(str).str.strip().str.upper())
            .drop_duplicates(subset=["CHASIS_NORM"])
            .set_index("CHASIS_NORM")["COD INTERNO"]
        )
        cod_equipo_norm = df["COD_EQUIPO"].str.strip().str.upper()
        df["COD_EQUIPO"] = cod_equipo_norm.map(mapa_chasis_a_cod).fillna(df["COD_EQUIPO"])

    df["TIPO DE ACTIVIDAD"] = df[col_tp].astype(str).str.strip().str.upper()
    df["HR PROGRAMADAS"] = pd.to_numeric(df[col_hr_prog], errors="coerce").fillna(0) if col_hr_prog else 0.0
    df["HRS EJECUTADAS"] = pd.to_numeric(df[col_hr_ejec], errors="coerce").fillna(0) if col_hr_ejec else 0.0

    df = df.dropna(subset=["SEMANA", "COD_EQUIPO"]).copy()
    df["SEMANA"] = df["SEMANA"].astype(int)
    df["Ejecutado"] = df["HRS EJECUTADAS"] > 0

    return df


def cargar_kpis_consolidados(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, sheet_name=SHEET_KPIS, header=1)
    except Exception as e:
        raise ErrorDatosFlota(f"❌ No se pudo leer la hoja '{SHEET_KPIS}': {e}")

    df.columns = [str(c).strip() for c in df.columns]
    verificar_columnas(df, ["COD EQUIPO"], SHEET_KPIS)
    df = df.dropna(subset=["COD EQUIPO"]).copy()

    columnas_numericas = [
        "Tiempo Mant. Prev.", "Tiempo Mant. Corr.", "Tiempo Inop.",
        "Cantidad de Fallas", "TPR", "TPF", "MTBF", "MTTR", "MTTF",
        "% Disponibilidad", "% DM", "DM GARANTIZADA",
    ]
    for c in columnas_numericas:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            print(f"⚠️  Aviso: la hoja '{SHEET_KPIS}' no tiene la columna '{c}'. Se rellenará con 0.")
            df[c] = 0.0

    df["Cumple_Meta_DM"] = df["% DM"] >= df["DM GARANTIZADA"]
    df["Brecha_DM_pp"] = (df["% DM"] - df["DM GARANTIZADA"]) * 100

    return df


def cargar_sos(path: str):
    try:
        df = pd.read_excel(path, sheet_name=SHEET_SOS)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except (ValueError, KeyError, FileNotFoundError):
        return None


# ==============================================================================
# B. MOTOR DE CÁLCULO Y CLASIFICACIÓN DE GRUPOS
# ==============================================================================

def clasificar_categoria_flota(codigo_equipo: str, contrato_gold: str) -> str:
    """
    Clasifica cada equipo por Tipo de Flota / Condición usando la columna real
    "Contrato_Gold" de la hoja PARQUE DE EQUIPOS (ya limpiada en
    `cargar_parque_equipos`): SI -> unidad bajo Contrato Gold (CONTRATO / Propio);
    cualquier otro valor (NO / NO ESPECIFICADO) -> CLIENTE. Los 3 códigos T- son
    unidades de alquiler identificadas manualmente (conocimiento de negocio, no
    derivable de una columna) y tienen prioridad sobre el dato de Contrato_Gold.
    Nota: esta operación NO cuenta con múltiples clientes distintos por equipo en el
    Excel de origen (todo el parque pertenece al contrato STRACON-Antamina); "CLIENTE"
    aquí distingue unidades fuera del Contrato Gold, no un cliente diferente.
    """
    eq = str(codigo_equipo).strip().upper()
    cg = str(contrato_gold).strip().upper()

    if eq in ["CV-T1002", "CV-T1006", "CV-T1009"]:
        return "ALQUILADOS"
    elif cg == "SI":
        return "CONTRATO"
    else:
        return "CLIENTE"


def _fusionar_horas_en_ventana(intervalos: list, ventana_inicio: pd.Timestamp, ventana_fin: pd.Timestamp) -> float:
    """
    Recorta cada intervalo (ini, fin) a los bordes de la ventana evaluada y fusiona
    los que se traslapan, para no duplicar horas de parada — mismo algoritmo de
    fusión ya usado en `calcular_matriz_criticidad_semanal`, aplicado sobre un
    listado de intervalos ya acotado a una sola clasificación (Preventivo o
    Correctivo, por separado).
    """
    clipeados = []
    for ini, fin in intervalos:
        ini_c = max(ini, ventana_inicio)
        fin_c = min(fin, ventana_fin)
        if fin_c > ini_c:
            clipeados.append((ini_c, fin_c))

    if not clipeados:
        return 0.0

    clipeados.sort(key=lambda x: x[0])
    fusionados = [list(clipeados[0])]
    for ini, fin in clipeados[1:]:
        if ini <= fusionados[-1][1]:
            fusionados[-1][1] = max(fusionados[-1][1], fin)
        else:
            fusionados.append([ini, fin])

    return sum((f - i).total_seconds() / 3600 for i, f in fusionados)


def _equipo_tiene_falla_abierta(codigo_equipo: str, df_int: pd.DataFrame) -> bool:
    """
    True si el equipo tiene una intervención CORRECTIVA sin cerrar — columna
    "H. FIN INTERV." (Fecha/Hora Fin de Entrega Real) vacía/NaT. Deliberadamente NO se
    usa "H. INICIO INTERV." (Fecha/Hora de Atención en Taller) como cierre: esa
    columna marca cuándo el equipo ENTRÓ a taller, no cuándo se le hizo la entrega
    real — confundirlas marcaría como "abierto" un evento que ya se cerró.

    Es SOLO un indicador visual de estado operativo en tiempo real ("FALLA EN
    CURSO" en la tabla) — NUNCA dispara ni sobreescribe el cálculo de %DM/MTBF/MTTR/
    Fallas de ningún equipo. Para el periodo oficial cerrado, esas cifras siguen
    siendo estrictamente las de la hoja "KPIs" tal cual, sin excepción (ver REGLA
    MAESTRA en `construir_kpis_hibridos_por_equipo`).
    """
    eq_norm = str(codigo_equipo).strip().upper()
    df_eq = df_int[df_int["EQUIPO"].astype(str).str.strip().str.upper() == eq_norm]
    if df_eq.empty:
        return False
    abiertas = df_eq[df_eq["H. FIN INTERV."].isna() & df_eq["H. INICIO INTERV."].notna()]
    if abiertas.empty:
        return False
    tipos = abiertas["TIPO DE INTERVENCION"].astype(str).str.upper()
    return bool(tipos.str.contains("CORRECTIV|FALLA|EMERGENCIA", regex=True, na=False).any())


def calcular_kpis_fallback_dinamico(codigo_equipo: str, df_int: pd.DataFrame, horas_mes: float = None) -> dict:
    """
    FALLBACK DE CÁLCULO DINÁMICO — réplica en Python de la Macro VBA
    `CalcularKPIsCompletos`, exclusiva para equipos SIN fila en la hoja "KPIs" (p.ej.
    flota CLIENTE/fuera de Contrato Gold, ver `clasificar_categoria_flota`, como
    CV-00367). REGLA MAESTRA (inmutable): si el equipo TIENE fila oficial, este
    cálculo NUNCA se ejecuta y NUNCA sobreescribe ese valor — ni siquiera si el
    equipo tiene una falla en curso (ver `_equipo_tiene_falla_abierta`, que es solo
    un badge visual, independiente de este cálculo). La regla es idéntica para toda
    la flota, nunca un caso especial por código de equipo.

    Filtra "Registro de Intervenciones" por equipo + columna de aplicabilidad == "SI",
    clasifica cada intervención en PREVENTIVO/CORRECTIVO (columna TIPO DE INTERVENCION
    contiene CORRECTIV/FALLA/EMERGENCIA -> Correctivo), acota a una VENTANA MÓVIL
    ("últimas horas_mes horas terminando ahora" — no un mes calendario fijo, para que
    una falla abierta que arrancó a fin del mes anterior no se recorte en el borde del
    mes) y fusiona traslapes por separado en cada grupo antes de sumar horas — así una
    parada de 3 días no cuenta como 3 eventos ni se duplica si hay registros solapados.

    NOTA — nombre de columna: la Macro la llama "Aplica DM" (columna W); en el Excel
    real esa columna se llama "APLICA KPI" (verificado contra los datos de CV-00367).
    Se usa "APLICA DM" si existe, con fallback a "APLICA KPI"; si ninguna existe, no
    se filtra por aplicabilidad (se usan todas las intervenciones del equipo).

    NOTA — horas_mes: si no se pasa explícito, se usan las horas del mes calendario
    ACTUAL (días_del_mes_de_hoy × 24 — ej. agosto = 31 días × 24 = 744h), como ventana
    móvil que termina en el momento en que se genera el dashboard.

    Retorna None si el equipo no tiene ninguna intervención utilizable (no hay con qué
    calcular; el llamador debe dejar el KPI en None/"SIN DATO", nunca forzarlo a 0).
    """
    eq_norm = str(codigo_equipo).strip().upper()
    df_eq = df_int[df_int["EQUIPO"].astype(str).str.strip().str.upper() == eq_norm].copy()

    col_aplica = None
    for candidato in ("APLICA DM", "APLICA KPI"):
        if candidato in df_eq.columns:
            col_aplica = candidato
            break
    if col_aplica:
        df_eq = df_eq[df_eq[col_aplica].astype(str).str.strip().str.upper() == "SI"]

    if df_eq.empty:
        return None

    ahora = pd.Timestamp.now()
    if horas_mes is None:
        dias_mes_actual = calendar.monthrange(ahora.year, ahora.month)[1]
        horas_mes = dias_mes_actual * 24.0
    ventana_fin = ahora
    ventana_inicio = ahora - pd.Timedelta(hours=horas_mes)

    intervalos_prev, intervalos_corr = [], []
    fallas = 0

    for _, r in df_eq.iterrows():
        # Columna H tal cual la Macro VBA ('fInicioInterv = ...Cells(j, "H")') — NO
        # "H_INICIO_REAL"/"H. PARADA" (nunca leída por la Macro real).
        ini = r.get("H. INICIO INTERV.")
        fin = r.get("H. FIN INTERV.")
        if pd.isna(ini):
            continue
        if pd.isna(fin):
            fin = ahora
        if fin <= ini:
            continue
        # Solo se procesan (para horas Y para el conteo de fallas) las intervenciones
        # que efectivamente tocan la ventana del mes evaluado.
        if ini >= ventana_fin or fin <= ventana_inicio:
            continue

        tipo = str(r.get("TIPO DE INTERVENCION", "") or "").upper()
        es_correctivo = any(k in tipo for k in ("CORRECTIV", "FALLA", "EMERGENCIA"))

        if es_correctivo:
            intervalos_corr.append((ini, fin))
            fallas += 1
        else:
            intervalos_prev.append((ini, fin))

    hrs_prev = _fusionar_horas_en_ventana(intervalos_prev, ventana_inicio, ventana_fin)
    hrs_corr = _fusionar_horas_en_ventana(intervalos_corr, ventana_inicio, ventana_fin)
    total_downtime = hrs_prev + hrs_corr
    horas_operativas = max(0.0, horas_mes - total_downtime)

    mttr = (hrs_corr / fallas) if fallas > 0 else 0.0
    mtbf = (horas_operativas / fallas) if fallas > 0 else horas_operativas
    pct_dm = (horas_operativas / horas_mes) * 100 if horas_mes > 0 else 0.0

    return {
        "dm": round(pct_dm, 2),
        "mtbf": round(mtbf, 1),
        "mttr": round(mttr, 1),
        "fallas": fallas,
        "horas_inoperativas": round(total_downtime, 2),
        "ventana_desde": ventana_inicio.strftime("%Y-%m-%d %H:%M"),
        "ventana_hasta": ventana_fin.strftime("%Y-%m-%d %H:%M"),
        "horas_mes": round(horas_mes, 1),
    }


def calcular_kpis_dinamico_periodo(codigo_equipo: str, fecha_desde, fecha_hasta, df_int: pd.DataFrame) -> dict:
    """
    RÉPLICA EXACTA (verificada contra el código VBA real) de las macros
    `CalcularKPIsCompletos` / `CalcularDisponibilidadDefinitiva`, para un rango de
    fechas EXPLÍCITO (los selectores DESDE/HASTA del dashboard) — a diferencia de
    `calcular_kpis_fallback_dinamico` (ventana móvil interna, solo para equipos sin
    fila en "KPIs"), esta función recibe el rango tal cual lo elige el usuario y es
    la FUENTE ÚNICA DE VERDAD para %DM/MTBF/MTTR/Fallas de CUALQUIER equipo —
    Contrato o Cliente — cuando se filtra por fecha.

    IMPORTANTE — esta función es la implementación de REFERENCIA en Python (para
    pruebas/CLI); el dashboard generado es un archivo HTML estático sin servidor
    Python corriendo, así que cuando el usuario mueve DESDE/HASTA en el navegador no
    hay proceso Python que reaccione. La reactividad real ocurre en JavaScript, en
    `calcularKpisDinamico()` dentro del HTML generado — una réplica línea por línea
    de este mismo algoritmo. Si se modifica uno, el otro debe actualizarse igual.

    Algoritmo (idéntico al VBA, línea por línea):
      1. fechaInicioFiltro = fecha_desde a las 00:00:00; fechaFinFiltro = fecha_hasta + 1
         día a las 00:00:00; horasMes = horas entre ambas.
      2. Filtra "Registro de Intervenciones" por equipo + columna de aplicabilidad
         ("Aplica DM"/"APLICA KPI") == "SI".
      3. Inicio = Columna H ("H. INICIO INTERV.", exactamente `wsRegistro.Cells(j,"H")`
         en el VBA) — NO "H. PARADA" (columna G), que la Macro real NUNCA lee. Fin =
         Columna I ("H. FIN INTERV."), o `ahora` si está vacío (marca
         `falla_en_curso=True`).
         NOTA DE CALIDAD DE DATO: "H. PARADA" puede tener typos no detectados por
         nadie (ej. CV-00451 tenía "2026-01-08" en vez de "2026-08-02" en esa
         columna, mientras "H. INICIO INTERV." sí estaba correcta) — usar la columna
         que la Macro realmente usa evita ese problema de raíz, sin necesidad de
         ningún guardia/validación adicional.
      4. Incluye la intervención solo si se traslapa con el filtro: inicio < fechaFinFiltro
         y fin > fechaInicioFiltro.
      5. Clasifica CORRECTIVO (TIPO DE INTERVENCION contiene CORRECTIV/FALLA/EMERGENCIA)
         vs PREVENTIVO.
      6. Fusiona traslapes por separado (Preventivo/Correctivo), acotados al rango.
      7. %DM = (horasMes - horas_inoperativas_totales) / horasMes × 100; MTBF/MTTR con
         el conteo real de eventos correctivos.
    """
    fecha_inicio_filtro = pd.Timestamp(fecha_desde).normalize()
    fecha_fin_filtro = pd.Timestamp(fecha_hasta).normalize() + pd.Timedelta(days=1)
    horas_mes = (fecha_fin_filtro - fecha_inicio_filtro).total_seconds() / 3600.0

    eq_norm = str(codigo_equipo).strip().upper()
    df_eq = df_int[df_int["EQUIPO"].astype(str).str.strip().str.upper() == eq_norm]

    col_aplica = None
    for candidato in ("APLICA DM", "APLICA KPI"):
        if candidato in df_eq.columns:
            col_aplica = candidato
            break
    if col_aplica:
        df_eq = df_eq[df_eq[col_aplica].astype(str).str.strip().str.upper() == "SI"]

    ahora = pd.Timestamp.now()
    intervalos_prev, intervalos_corr = [], []
    fallas = 0
    falla_en_curso = False

    for _, r in df_eq.iterrows():
        # Columna H de "Registro de Intervenciones" ('fInicioInterv'), exactamente como
        # la lee la Macro VBA — NO "H. PARADA" (columna G, nunca leída por la Macro; ver
        # nota de calidad de dato más abajo, CV-00451).
        ini = r.get("H. INICIO INTERV.")
        fin = r.get("H. FIN INTERV.")
        if pd.isna(ini):
            continue
        abierta = pd.isna(fin)
        if abierta:
            fin = ahora
        if fin <= ini:
            continue
        if not (ini < fecha_fin_filtro and fin > fecha_inicio_filtro):
            continue

        tipo = str(r.get("TIPO DE INTERVENCION", "") or "").upper()
        es_correctivo = any(k in tipo for k in ("CORRECTIV", "FALLA", "EMERGENCIA"))

        if es_correctivo:
            intervalos_corr.append((ini, fin))
            fallas += 1
            if abierta:
                falla_en_curso = True
        else:
            intervalos_prev.append((ini, fin))

    hrs_prev = _fusionar_horas_en_ventana(intervalos_prev, fecha_inicio_filtro, fecha_fin_filtro)
    hrs_corr = _fusionar_horas_en_ventana(intervalos_corr, fecha_inicio_filtro, fecha_fin_filtro)
    hrs_inop_total = hrs_prev + hrs_corr
    hrs_operativas = max(0.0, horas_mes - hrs_inop_total)

    mttr = (hrs_corr / fallas) if fallas > 0 else 0.0
    mtbf = (hrs_operativas / fallas) if fallas > 0 else hrs_operativas
    pct_dm = max(0.0, (horas_mes - hrs_inop_total) / horas_mes) * 100.0 if horas_mes > 0 else 0.0

    return {
        "dm": round(pct_dm, 2),
        "mtbf": round(mtbf, 1),
        "mttr": round(mttr, 1),
        "fallas": fallas,
        "horas_inoperativas": round(hrs_inop_total, 2),
        "falla_en_curso": falla_en_curso,
    }


def construir_kpis_hibridos_por_equipo(df_kpis: pd.DataFrame, df_parque: pd.DataFrame, df_int: pd.DataFrame) -> dict:
    """
    ÚNICA FUENTE DE VERDAD de KPIs por equipo para TODO el dashboard (tabla "Estado de
    Confiabilidad por Unidad", Matriz de Criticidad, catálogo de equipos usado por el
    resto de gráficos JS). Estrategia híbrida:
      1. Equipo CON fila en la hoja KPIs: valores oficiales tal cual (MTTR/MTBF
         priorizan 'TPR'/'TPF' sobre 'MTTR'/'MTBF', ver nota en el bucle de abajo).
      2. Equipo SIN fila en KPIs (típicamente flota CLIENTE/fuera de Contrato Gold,
         ej. CV-00367): `calcular_kpis_fallback_dinamico` sobre el Registro de
         Intervenciones (réplica de la Macro VBA).
    Se calcula UNA sola vez aquí; ningún otro componente debe releer df_kpis
    directamente ni recalcular por su cuenta — así se evita que dos gráficos muestren
    números distintos para el mismo equipo.

    Retorna dict {codigo_equipo: {dm, mtbf, mttr, fallas, dm_meta, contrato_gold,
    categoria, es_calculo_dinamico}}, con `None` en dm/mtbf/mttr/fallas cuando el
    equipo no tiene NI fila oficial NI intervenciones utilizables para el fallback.
    """
    meta_dict = dict(zip(df_kpis["COD EQUIPO"], df_kpis["DM GARANTIZADA"]))
    contrato_gold_dict = dict(zip(df_parque["COD INTERNO"], df_parque["Contrato_Gold"]))

    kpis_oficiales_dict = {}
    for _, r in df_kpis.iterrows():
        eq_cod = str(r["COD EQUIPO"])
        # MTTR/MTBF se leen prioritariamente de 'TPR'/'TPF' (columnas reales de la hoja
        # KPIs con el valor correcto por equipo, ej. CV-00451 TPR=2.09h); las columnas
        # 'MTTR'/'MTBF' quedan solo como respaldo si 'TPR'/'TPF' no existen o vienen
        # vacías para esa fila.
        mtbf_val = r["TPF"] if pd.notnull(r["TPF"]) else r["MTBF"]
        mttr_val = r["TPR"] if pd.notnull(r["TPR"]) else r["MTTR"]
        kpis_oficiales_dict[eq_cod] = {
            "dm": round(float(r["% DM"]) * 100, 2) if pd.notnull(r["% DM"]) else None,
            "mtbf": round(float(mtbf_val), 1) if pd.notnull(mtbf_val) else None,
            "mttr": round(float(mttr_val), 1) if pd.notnull(mttr_val) else None,
            "fallas": int(r["Cantidad de Fallas"]) if pd.notnull(r["Cantidad de Fallas"]) else None,
            "horas_inoperativas": round(float(r["Tiempo Inop."]), 2) if pd.notnull(r.get("Tiempo Inop.")) else None,
        }

    resultado = {}
    for eq in sorted(df_parque["COD INTERNO"].unique()):
        contrato_gold_val = str(contrato_gold_dict.get(eq, "NO ESPECIFICADO"))
        categoria_calc = clasificar_categoria_flota(eq, contrato_gold_val)
        oficial = kpis_oficiales_dict.get(eq, {})

        # REGLA MAESTRA (inmutable): si el equipo tiene fila en la hoja KPIs, ese valor
        # oficial se usa TAL CUAL en la tabla/tarjetas — nunca se sobreescribe con un
        # recálculo dinámico, ni siquiera si el equipo tiene una falla en curso. El
        # fallback dinámico se activa ÚNICAMENTE cuando no hay fila oficial (ver
        # `calcular_kpis_fallback_dinamico`, típicamente flota Cliente/fuera de
        # Contrato Gold, ej. CV-00367). Regla única e idéntica para toda la flota.
        es_calculo_dinamico = False
        sin_dato_oficial = oficial.get("dm") is None or oficial.get("mtbf") is None or oficial.get("mttr") is None
        if sin_dato_oficial:
            fallback = calcular_kpis_fallback_dinamico(eq, df_int)
            if fallback is not None:
                oficial = {**oficial, **{k: v for k, v in fallback.items() if k in ("dm", "mtbf", "mttr", "fallas", "horas_inoperativas")}}
                es_calculo_dinamico = True

        # "Falla en curso" — INDICADOR VISUAL de estado operativo en tiempo real, 100%
        # independiente del valor numérico mostrado: un equipo con una intervención
        # correctiva sin "Fecha/Hora Fin de Entrega Real" (H. FIN INTERV. vacío, ej.
        # CV-00419) se marca así aunque su %DM/MTBF/MTTR sigan siendo los oficiales del
        # periodo cerrado en KPIs. Nunca cambia el número — solo el badge.
        falla_en_curso = _equipo_tiene_falla_abierta(eq, df_int)

        resultado[eq] = {
            "dm": oficial.get("dm"),
            "mtbf": oficial.get("mtbf"),
            "mttr": oficial.get("mttr"),
            "fallas": oficial.get("fallas"),
            "horas_inoperativas": oficial.get("horas_inoperativas"),
            "dm_meta": round(float(meta_dict.get(eq, 0.88)) * 100, 1),
            "contrato_gold": contrato_gold_val,
            "categoria": categoria_calc,
            "es_calculo_dinamico": es_calculo_dinamico,
            "falla_en_curso": falla_en_curso,
        }

    return resultado


def kpis_globales_flota(df_kpis: pd.DataFrame) -> dict:
    horas_totales = (df_kpis["TPF"] + df_kpis["TPR"]).sum()

    disponibilidad_ponderada = (
        df_kpis["TPF"].sum() / horas_totales * 100 if horas_totales > 0 else 0
    )
    total_fallas = df_kpis["Cantidad de Fallas"].sum()
    mtbf_ponderado = (df_kpis["TPF"].sum() / total_fallas) if total_fallas > 0 else 0
    mttr_ponderado = (df_kpis["TPR"].sum() / total_fallas) if total_fallas > 0 else 0

    return {
        "unidades": int(len(df_kpis)),
        "dm_global": round(float(disponibilidad_ponderada), 1),
        "mtbf_global": round(float(mtbf_ponderado), 1),
        "mttr_global": round(float(mttr_ponderado), 1),
        "total_fallas": int(total_fallas),
        "fuera_meta": int((~df_kpis["Cumple_Meta_DM"]).sum()),
    }


def calcular_diccionario_semanas_pm(df_plan: pd.DataFrame) -> dict:
    es_pm = df_plan["TIPO DE ACTIVIDAD"].str.contains("PREVENTIVO", case=False, na=False)
    df_pm = df_plan[es_pm].copy()

    semanas = sorted(df_pm["SEMANA"].unique())
    resumen_semanas = {}

    for sem in semanas:
        df_sem = df_pm[df_pm["SEMANA"] == sem]
        prog = len(df_sem)
        ejec = len(df_sem[df_sem["HRS EJECUTADAS"] > 0])
        pct = round((ejec / prog * 100), 1) if prog > 0 else 0.0

        resumen_semanas[str(sem)] = {
            "programados": prog,
            "ejecutados": ejec,
            "pct": pct
        }

    return resumen_semanas


def calcular_resumen_horas_pm_semanal(df_plan: pd.DataFrame) -> pd.DataFrame:
    """Agrega Horas Programadas vs Ejecutadas de PM por semana (para trendline)."""
    es_pm = df_plan["TIPO DE ACTIVIDAD"].str.contains("PREVENTIVO", case=False, na=False)
    df_pm = df_plan[es_pm].copy()

    resumen = (
        df_pm.groupby("SEMANA")
        .agg(
            Horas_Programadas=("HR PROGRAMADAS", "sum"),
            Horas_Ejecutadas=("HRS EJECUTADAS", "sum"),
            Tareas_Programadas=("HRS EJECUTADAS", "count"),
            Tareas_Ejecutadas=("Ejecutado", "sum"),
        )
        .reset_index()
        .sort_values("SEMANA")
    )
    resumen["Pct_Cumplimiento"] = np.where(
        resumen["Tareas_Programadas"] > 0,
        (resumen["Tareas_Ejecutadas"] / resumen["Tareas_Programadas"] * 100).round(1),
        0.0
    )
    return resumen


def pareto_sistemas(df_int: pd.DataFrame) -> pd.DataFrame:
    if "SISTEMA" not in df_int.columns or "TIPO DE INTERVENCION" not in df_int.columns:
        return pd.DataFrame(columns=["SISTEMA", "Horas_Parada", "N_Eventos", "Pct_Acumulado"])

    correctivos = df_int[
        df_int["TIPO DE INTERVENCION"].astype(str).str.contains("CORRECTIV", na=False)
    ].dropna(subset=["SISTEMA"])

    resumen = (
        correctivos.groupby("SISTEMA")
        .agg(
            Horas_Parada=("Horas_Reparacion_Neta", "sum"),
            N_Eventos=("Horas_Reparacion_Neta", "count"),
        )
        .sort_values("Horas_Parada", ascending=False)
        .reset_index()
    )

    total = resumen["Horas_Parada"].sum()
    if total > 0:
        resumen["Pct_Acumulado"] = (resumen["Horas_Parada"].cumsum() / total * 100).round(1)
    else:
        resumen["Pct_Acumulado"] = 0.0

    resumen["MTTR_Sistema"] = (resumen["Horas_Parada"] / resumen["N_Eventos"].replace(0, np.nan)).fillna(0).round(2)
    # Score de criticidad compuesto: pondera magnitud (horas) y frecuencia (eventos) por igual,
    # normalizados 0-1, para el filtro "Top Criticidad" del mini-toolbar del Pareto.
    max_h = resumen["Horas_Parada"].max() or 1
    max_e = resumen["N_Eventos"].max() or 1
    resumen["Criticidad_Score"] = (
        0.5 * (resumen["Horas_Parada"] / max_h) + 0.5 * (resumen["N_Eventos"] / max_e)
    ).round(3)

    return resumen


def calcular_matriz_semana_sistema(df_int: pd.DataFrame) -> dict:
    """Horas de inoperatividad (correctivos) agrupadas por [Semana][Sistema], para el
    filtro local de semana del donut de Inoperatividad. La clave 'ALL' contiene el
    agregado de todas las semanas (idéntico criterio que pareto_sistemas)."""
    if "SISTEMA" not in df_int.columns or "TIPO DE INTERVENCION" not in df_int.columns:
        return {"ALL": {}}

    correctivos = df_int[
        df_int["TIPO DE INTERVENCION"].astype(str).str.contains("CORRECTIV", na=False)
    ].dropna(subset=["SISTEMA"])

    matriz = {}
    resumen_all = correctivos.groupby("SISTEMA")["Horas_Reparacion_Neta"].sum()
    matriz["ALL"] = {str(k): round(float(v), 2) for k, v in resumen_all.items()}

    if "SEMANA" in correctivos.columns:
        for sem, df_sem in correctivos.groupby("SEMANA"):
            if pd.isna(sem):
                continue
            resumen_sem = df_sem.groupby("SISTEMA")["Horas_Reparacion_Neta"].sum()
            matriz[str(int(sem))] = {str(k): round(float(v), 2) for k, v in resumen_sem.items()}

    return matriz


def calcular_dias_sin_falla(df_int: pd.DataFrame, equipos: list) -> dict:
    """Calcula días transcurridos desde la última falla correctiva registrada, por equipo."""
    resultado = {}
    if "TIPO DE INTERVENCION" not in df_int.columns or "FECHA" not in df_int.columns:
        return {eq: None for eq in equipos}

    correctivos = df_int[df_int["TIPO DE INTERVENCION"].astype(str).str.contains("CORRECTIV", na=False)]
    fecha_referencia = df_int["FECHA"].max()
    if pd.isna(fecha_referencia):
        fecha_referencia = pd.Timestamp.now()

    ultima_falla_por_equipo = correctivos.groupby("EQUIPO")["FECHA"].max()

    for eq in equipos:
        if eq in ultima_falla_por_equipo.index and pd.notnull(ultima_falla_por_equipo[eq]):
            dias = (fecha_referencia - ultima_falla_por_equipo[eq]).days
            resultado[eq] = int(max(0, dias))
        else:
            resultado[eq] = None
    return resultado


def calcular_tendencia_semanal_flota(df_int: pd.DataFrame, df_parque: pd.DataFrame, equipos_filtro: list = None) -> pd.DataFrame:
    """
    Serie semanal aproximada de %DM de flota y N° de fallas, para los sparklines de las
    tarjetas KPI superiores. Es un indicador ILUSTRATIVO de tendencia, calculado con el
    mismo principio de fusión de intervalos que el cálculo oficial, pero agregado por
    semana calendario completa (168 h) en vez del rango exacto seleccionado por el
    usuario en los filtros. NO reemplaza ni altera el %DM oficial mostrado en las
    tarjetas/tabla, que sigue el algoritmo JS `calcularHorasInopExactas` sobre el rango
    de fechas que el usuario elija.

    `equipos_filtro`: subconjunto opcional de equipos (p.ej. solo "ALQUILADOS") para
    calcular la tendencia de esa subflota específica — por defecto usa TODO el parque,
    igual que antes (cambio aditivo, no rompe ningún llamado existente).
    """
    equipos = sorted(equipos_filtro) if equipos_filtro is not None else sorted(df_parque["COD INTERNO"].unique())
    if "SEMANA" not in df_int.columns or df_int["SEMANA"].dropna().empty or not equipos:
        return pd.DataFrame(columns=["SEMANA", "DM_pct", "Fallas"])

    semanas = sorted(df_int["SEMANA"].dropna().unique())
    filas = []

    for sem in semanas:
        df_sem = df_int[(df_int["SEMANA"] == sem) & (df_int["EQUIPO"].isin(equipos))]
        inop_total = 0.0
        for eq in equipos:
            df_eq = df_sem[df_sem["EQUIPO"] == eq]
            intervalos = []
            for _, r in df_eq.iterrows():
                ini = r.get("H_INICIO_REAL")
                fin = r.get("H. FIN INTERV.")
                if pd.isna(ini):
                    continue
                if pd.isna(fin):
                    fin = ini + pd.Timedelta(hours=float(r.get("Horas_Reparacion_Neta", 0) or 0))
                if pd.notnull(ini) and pd.notnull(fin) and fin > ini:
                    intervalos.append((ini, fin))
            if not intervalos:
                continue
            intervalos.sort(key=lambda x: x[0])
            merged = [list(intervalos[0])]
            for ini, fin in intervalos[1:]:
                if ini <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], fin)
                else:
                    merged.append([ini, fin])
            inop_total += sum((f - i).total_seconds() / 3600 for i, f in merged)

        horas_periodo_semana = 168.0 * max(len(equipos), 1)
        dm_semana = max(0.0, min(100.0, (horas_periodo_semana - inop_total) / horas_periodo_semana * 100)) if horas_periodo_semana > 0 else 0.0

        # BUG FIX (dentro de este indicador ilustrativo): el conteo de fallas ahora se
        # acota al mismo subconjunto de equipos que el cálculo de horas inoperativas
        # (antes contaba fallas de TODA la flota sin importar `equipos_filtro`).
        fallas_semana = int(
            df_sem[df_sem["TIPO DE INTERVENCION"].astype(str).str.contains("CORRECTIV", na=False)].shape[0]
        ) if "TIPO DE INTERVENCION" in df_sem.columns else 0

        filas.append({"SEMANA": int(sem), "DM_pct": round(dm_semana, 1), "Fallas": fallas_semana})

    return pd.DataFrame(filas)


def calcular_matriz_criticidad_semanal(df_int: pd.DataFrame, equipos: list) -> dict:
    """
    MTBF/MTTR/%DM/N° de Fallas por EQUIPO y por SEMANA. Mismo principio ILUSTRATIVO
    (fusión de intervalos acotada a semana calendario completa de 168 h) que
    `calcular_tendencia_semanal_flota`, pero desagregado por equipo en vez de a nivel
    de flota. NO reemplaza ni altera el MTBF/MTTR/%DM oficial (global, hoja KPIs) que
    se muestra en la vista "Acumulado Total"; es una vista adicional por semana,
    reutilizada tanto por el filtro de semana de la Matriz de Criticidad (MTBF/MTTR)
    como por el filtro de semana del Velocímetro de DM Global (dm_pct).
    """
    resultado = {}
    if "SEMANA" not in df_int.columns or df_int["SEMANA"].dropna().empty:
        return resultado

    tiene_tipo = "TIPO DE INTERVENCION" in df_int.columns
    semanas = sorted(df_int["SEMANA"].dropna().unique())

    for sem in semanas:
        df_sem = df_int[df_int["SEMANA"] == sem]
        filas_semana = []
        for eq in equipos:
            df_eq = df_sem[df_sem["EQUIPO"] == eq]
            intervalos = []
            for _, r in df_eq.iterrows():
                ini = r.get("H_INICIO_REAL")
                fin = r.get("H. FIN INTERV.")
                if pd.isna(ini):
                    continue
                if pd.isna(fin):
                    fin = ini + pd.Timedelta(hours=float(r.get("Horas_Reparacion_Neta", 0) or 0))
                if pd.notnull(ini) and pd.notnull(fin) and fin > ini:
                    intervalos.append((ini, fin))

            inop = 0.0
            if intervalos:
                intervalos.sort(key=lambda x: x[0])
                merged = [list(intervalos[0])]
                for ini, fin in intervalos[1:]:
                    if ini <= merged[-1][1]:
                        merged[-1][1] = max(merged[-1][1], fin)
                    else:
                        merged.append([ini, fin])
                inop = sum((f - i).total_seconds() / 3600 for i, f in merged)

            fallas = int(
                df_eq[df_eq["TIPO DE INTERVENCION"].astype(str).str.contains("CORRECTIV", na=False)].shape[0]
            ) if tiene_tipo else 0

            operativas = max(0.0, 168.0 - inop)
            mtbf = (operativas / fallas) if fallas > 0 else operativas
            mttr = (inop / fallas) if fallas > 0 else 0.0
            dm_pct = max(0.0, min(100.0, (operativas / 168.0) * 100))

            filas_semana.append({
                "equipo": eq,
                "mtbf": round(mtbf, 1),
                "mttr": round(mttr, 1),
                "fallas": fallas,
                "dm_pct": round(dm_pct, 1)
            })

        resultado[str(int(sem))] = filas_semana

    return resultado


def preparar_raw_intervenciones_js(df_intervenciones: pd.DataFrame) -> list:
    datos = []
    if "APLICA DM" in df_intervenciones.columns:
        df_filter = df_intervenciones[df_intervenciones["APLICA DM"].astype(str).str.upper() == "SI"].copy()
    else:
        df_filter = df_intervenciones.copy()

    for _, r in df_filter.iterrows():
        f = r.get("FECHA")
        # Columna H de "Registro de Intervenciones" tal cual la usa la Macro VBA
        # ('fInicioInterv = wsRegistro.Cells(j, "H").Value') — NO "H. PARADA" (columna G,
        # nunca leída por la Macro; puede traer typos no detectados, ej. CV-00451 con
        # "2026-01-08" en vez de "2026-08-02" en H. PARADA, mientras H. INICIO INTERV.
        # estaba correcta).
        i = r.get("H. INICIO INTERV.")
        fn = r.get("H. FIN INTERV.")
        sem = r.get("SEMANA")
        sistema_val = r.get("SISTEMA")
        sistema_str = "" if pd.isna(sistema_val) else str(sistema_val).strip()

        str_fecha = f.strftime("%Y-%m-%d") if pd.notnull(f) else ""
        str_inicio = i.strftime("%Y-%m-%dT%H:%M:%S") if pd.notnull(i) else ""
        str_fin = fn.strftime("%Y-%m-%dT%H:%M:%S") if pd.notnull(fn) else ""

        datos.append({
            "equipo": str(r.get("EQUIPO", "")),
            "tipo": str(r.get("TIPO DE INTERVENCION", "")),
            "sistema": sistema_str,
            "semana": int(sem) if pd.notnull(sem) else 0,
            "fecha": str_fecha,
            "inicio": str_inicio,
            "fin": str_fin,
            "horas_netas": float(r.get("Horas_Reparacion_Neta", 0) or 0)
        })
    return datos


# ==============================================================================
# C. GENERADOR DE PRESENTACIÓN INTERACTIVA (HTML5)
# ==============================================================================

def construir_banner_tecnico_fmx() -> str:
    """
    Ficha técnica del Volvo FMX — Motor D13C (540 HP): imagen técnica real del motor
    (incrustada en Base64 para que el HTML siga siendo un único archivo autocontenido,
    sin depender de la ruta de red en tiempo de visualización) + tarjetas de
    especificación. Puramente informativo/estático — no participa en ningún cálculo
    del dashboard. Paleta "Cyber-Industrial" específica de esta sección (independiente
    de la paleta Deep Navy del resto del dashboard, según especificación): fondo
    #0d1117, acento primario #00b4d8 (cian), acento secundario #ffd166 (ámbar).
    """
    try:
        with open(RUTA_IMAGEN_MOTOR_D13C, "rb") as f:
            imagen_motor_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"⚠️  Aviso: no se pudo cargar la imagen técnica del motor D13C ({e}). El banner se mostrará sin imagen.")
        imagen_motor_b64 = ""

    if imagen_motor_b64:
        imagen_html = (
            f'<img src="data:image/png;base64,{imagen_motor_b64}" '
            f'style="width: 100%; max-width: 650px; height: auto; border-radius: 8px; '
            f'filter: drop-shadow(0px 4px 15px rgba(0, 180, 216, 0.2));" '
            f'alt="Esquema Técnico Motor Volvo D13C e I-Shift">'
        )
    else:
        imagen_html = (
            '<div class="tech-img-fallback">'
            '<i class="fa-solid fa-image-slash"></i> Imagen técnica no disponible'
            '</div>'
        )

    specs = [
        ("1", "MOTOR VOLVO D13C", "540 HP (403 kW) · Euro 5 · Torque 2600 Nm"),
        ("2", "FRENO DE MOTOR VEB+", "375 kW (510 HP) de frenado auxiliar"),
        ("3", "TRANSMISIÓN I-SHIFT", "Heavy Duty · 12 velocidades automatizada"),
        ("4", "EJES DE REDUCCIÓN DE CUBO", "Configuración 8x4 · mayor torque en rueda"),
        ("5", "TOLVA HARDOX", "Acero de alta resistencia al desgaste"),
    ]
    spec_cards_html = ""
    for num, titulo, detalle in specs:
        spec_cards_html += f"""
        <div class="tech-spec-card">
            <span class="tech-spec-num">{num}</span>
            <div>
                <div class="tech-spec-title">{titulo}</div>
                <div class="tech-spec-detail">{detalle}</div>
            </div>
        </div>
        """

    return f"""
    <div class="tech-banner" id="panel_tech_banner">
        <div class="tech-banner-header">
            <i class="fa-solid fa-truck-fast"></i>
            <div>
                <div class="tech-banner-title">FICHA TÉCNICA — VOLVO FMX · MOTOR D13C (540 HP)</div>
                <div class="tech-banner-subtitle">Anatomía del volquete · Configuración 8x4 R</div>
            </div>
        </div>
        <div class="tech-banner-body">
            <div class="tech-img-wrap">{imagen_html}</div>
            <div class="tech-spec-grid">{spec_cards_html}</div>
        </div>
    </div>
    """


def generar_y_abrir_dashboard(df_kpis: pd.DataFrame, df_int: pd.DataFrame, df_plan: pd.DataFrame, df_parque: pd.DataFrame):
    print("📊 Construyendo gráficos interactivos de clase mundial...")

    kpis_glob = kpis_globales_flota(df_kpis)

    # ÚNICA FUENTE DE VERDAD de KPIs por equipo (oficial de la hoja KPIs + fallback
    # dinámico para flota CLIENTE sin fila oficial) — se calcula UNA sola vez aquí y
    # la reutilizan la Matriz de Criticidad y el catálogo de equipos (tabla principal,
    # gauge, gráfico por equipo, etc.). Ningún componente vuelve a leer df_kpis
    # directamente ni recalcula por su cuenta.
    kpis_hibridos = construir_kpis_hibridos_por_equipo(df_kpis, df_parque, df_int)

    data_pm_semanas = calcular_diccionario_semanas_pm(df_plan)
    banner_tecnico_html = construir_banner_tecnico_fmx()

    # Módulo independiente MTBS (Mean Time Between Servicing) — ver sección D al
    # final del archivo. Solo LEE df_int/df_parque ya cargados; no modifica ni
    # depende de ningún cálculo de MTBF/MTTR/DM de las secciones A-C. Los
    # horómetros (mayo/junio/julio 2026) son una fuente EXCLUSIVA de este módulo.
    df_horometros = cargar_horometros_consolidado()
    df_mtbs_mensual = vw_mtbs_volvo_fmx(df_int, df_parque, periodo="M", df_horometros=df_horometros)
    df_volvo_connect = construir_fact_volvo_connect(RUTA_CARPETA_VOLVO_CONNECT, df_parque)
    mtbs_panel_html, mtbs_script_html = construir_panel_mtbs_html(df_mtbs_mensual, df_volvo_connect)

    # Módulo independiente Backlog — ver sección E al final del archivo. Solo LEE
    # la hoja DETALLE_BKL y df_parque (para el filtro Volvo FMX + categoría de flota);
    # no modifica ni depende de ningún cálculo de MTBF/MTTR/DM/Pareto ni del módulo
    # MTBS. "Gestión de Backlog" en tarjetas — una tarjeta por N_ITEM, con desglose de
    # repuestos, disponibilidad de almacén y los 2 KPI resumen (% Cumplimiento,
    # Pendientes); reemplaza al antiguo panel de barras por semana (retirado).
    items_bkl = cargar_detalle_bkl_items(ARCHIVO_ENTRADA, df_parque)
    bkl_cards_panel_html, bkl_cards_script_html = construir_panel_bkl_cards_html(items_bkl)

    # Módulo independiente Estado de Flota del Día — ver sección F al final del
    # archivo. Solo LEE df_int (ya cargado); no modifica ni depende de ningún
    # cálculo de MTBF/MTTR/DM/Pareto ni de los módulos MTBS/Backlog. Tarjeta que
    # se inserta junto al Velocímetro DM Global (misma fila).
    efd_panel_html, efd_script_html = construir_panel_estado_flota_dia_html(df_int)

    semanas = sorted(df_plan["SEMANA"].unique())
    if len(semanas) == 0:
        semanas = [0]
    ultima_semana = str(semanas[-1])
    datos_ultima_sem = data_pm_semanas.get(ultima_semana, {"programados": 0, "ejecutados": 0, "pct": 0.0})

    # Días sin falla por equipo (informativo, no es un KPI oficial ni cambia con el
    # filtro de fechas): se agrega a `catalogo_equipos` más abajo para que el gráfico
    # "Disponibilidad Mecánica vs. Meta" (ahora 100% JS-driven) lo tenga disponible.
    dias_sin_falla_dict = calcular_dias_sin_falla(df_int, sorted(df_parque["COD INTERNO"].unique()))

    # `pareto_sistemas` se conserva (Acumulado Total, TODAS las intervenciones) SOLO como
    # fuente de la paleta fija de colores por sistema del donut (`sistemas_top6_donut`/
    # `color_por_sistema_donut` más abajo) — el gráfico "Pareto de Sistemas Críticos" en
    # sí ahora se recalcula 100% en JS (`renderParetoChart`), reactivo a Fecha/Flota.
    df_pareto = pareto_sistemas(df_int)

    # --- Datos Gráfico 8b: Tendencia semanal por Tipo de Flota, para sparklines
    # reactivos de las tarjetas KPI superiores (barra de filtros del bloque KPI). Se
    # calcula UNA serie por categoría (ALL/CONTRATO/CLIENTE/ALQUILADOS) reutilizando
    # `clasificar_categoria_flota` (misma clasificación ya validada del Velocímetro/
    # Tabla), para que el JS solo tenga que elegir cuál dibujar — no recalcular nada.
    contrato_gold_dict_tmp = dict(zip(df_parque["COD INTERNO"], df_parque["Contrato_Gold"]))
    equipos_todos_tmp = sorted(df_parque["COD INTERNO"].unique())
    equipos_por_categoria = {"ALL": equipos_todos_tmp}
    for _cat in ["CONTRATO", "CLIENTE", "ALQUILADOS"]:
        equipos_por_categoria[_cat] = [
            eq for eq in equipos_todos_tmp
            if clasificar_categoria_flota(eq, contrato_gold_dict_tmp.get(eq, "NO ESPECIFICADO")) == _cat
        ]

    tendencias_por_categoria = {}
    for _cat, _equipos_lista in equipos_por_categoria.items():
        _df_t = calcular_tendencia_semanal_flota(df_int, df_parque, equipos_filtro=_equipos_lista)
        tendencias_por_categoria[_cat] = {
            "dm": _df_t["DM_pct"].tolist() if len(_df_t) else [],
            "fallas": _df_t["Fallas"].tolist() if len(_df_t) else [],
        }
    json_tendencias_categoria = json.dumps(tendencias_por_categoria)

    tendencia_dm_serie = tendencias_por_categoria["ALL"]["dm"]
    tendencia_fallas_serie = tendencias_por_categoria["ALL"]["fallas"]

    # --- Gráfico 3: Horas Reales vs Target PM ---
    df_pm_prev = df_plan[df_plan["TIPO DE ACTIVIDAD"].str.contains("PREVENTIVO", na=False)]

    fig_pm = go.Figure()
    num_semanas = len(semanas)
    for sem in semanas:
        df_sem = df_pm_prev[df_pm_prev["SEMANA"] == sem].groupby("COD_EQUIPO")[["HR PROGRAMADAS", "HRS EJECUTADAS"]].sum().reset_index()
        is_latest = (sem == semanas[-1])

        fig_pm.add_trace(go.Bar(
            x=df_sem["COD_EQUIPO"], y=df_sem["HR PROGRAMADAS"], name="Hrs Programadas",
            marker_color="rgba(100,116,139,0.65)", visible=is_latest,
            hovertemplate="<b>%{x}</b><br>Programadas: %{y:.1f} h<extra></extra>"
        ))
        fig_pm.add_trace(go.Bar(
            x=df_sem["COD_EQUIPO"], y=df_sem["HRS EJECUTADAS"], name="Hrs Ejecutadas",
            marker_color=COLOR_CYAN, visible=is_latest,
            hovertemplate="<b>%{x}</b><br>Ejecutadas: %{y:.1f} h<extra></extra>"
        ))

    buttons_pm = []
    for i, sem in enumerate(semanas):
        visible_mask = [False] * (num_semanas * 2)
        visible_mask[i * 2] = True
        visible_mask[i * 2 + 1] = True
        buttons_pm.append(dict(
            label=f"Semana {sem}", method="update",
            args=[{"visible": visible_mask}, {"title": f"<b>Desviación Mantenimiento Preventivo — Semana {sem}</b>"}]
        ))

    fig_pm.update_layout(
        updatemenus=[dict(
            type="dropdown", direction="down", active=num_semanas - 1,
            x=0.0, y=1.24, showactive=True, buttons=buttons_pm,
            font=dict(color=COLOR_ACCENT_BLUE, size=12), bgcolor=COLOR_PANEL
        )],
        title=f"<b>Desviación Mantenimiento Preventivo — Semana {semanas[-1]}</b>",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, Segoe UI, sans-serif", color="#e2e8f0"),
        hoverlabel=dict(bgcolor="rgba(21,28,44,0.95)", bordercolor="#38bdf8", font=dict(family="JetBrains Mono, monospace", size=12, color="#f8fafc")),
        hovermode="x unified",
        height=460,
        margin=dict(l=10, r=10, t=70, b=10)
    )

    # --- Gráfico 4 (v8 — JS-driven "Dashboard Executive Premium"): OTRAS ACTIVIDADES ---
    # Programado vs. Ejecutado por Tipo de Actividad, con paleta de pares de color
    # dedicada por tipo (en vez del fucsia único anterior), glow/profundidad vía CSS
    # y controles de semana en un mini-toolbar propio (mismo patrón JS-driven que
    # DM/Pareto/Matriz/Donut/Gauge). Ver `renderOtrosChart` en el <script>.
    df_otros = df_plan[~df_plan["TIPO DE ACTIVIDAD"].str.contains("PREVENTIVO", na=False)].copy()
    tipos_actividad = sorted(df_otros["TIPO DE ACTIVIDAD"].unique())

    # Pares de color Programado (oscuro/translúcido) vs. Ejecutado (vibrante/neón) por
    # tipo de actividad. Se cubren los 3 tipos pedidos explícitamente + CORRECTIVO
    # (presente en el Excel real pero no especificado) + un par de respaldo por si
    # aparece un tipo nuevo en el futuro.
    pares_color_actividad = {
        "BACKLOG": {"prog": "#334155", "ejec": "#FF007A"},
        "CAMPAÑA": {"prog": "#1e3a5f", "ejec": "#00E5FF"},
        "INSPECCION": {"prog": "#3b2a5e", "ejec": "#FFD700"},
        "CORRECTIVO": {"prog": "#4a1d1d", "ejec": "#FF6B35"},
        "_DEFAULT": {"prog": "#334155", "ejec": "#a78bfa"},
    }

    otros_data_list = []
    for sem in semanas:
        df_sem_otros = df_otros[df_otros["SEMANA"] == sem]
        for tipo in tipos_actividad:
            df_tipo = df_sem_otros[df_sem_otros["TIPO DE ACTIVIDAD"] == tipo].groupby("COD_EQUIPO")[["HR PROGRAMADAS", "HRS EJECUTADAS"]].sum().reset_index()
            for _, r in df_tipo.iterrows():
                otros_data_list.append({
                    "semana": int(sem),
                    "tipo": tipo,
                    "equipo": str(r["COD_EQUIPO"]),
                    "prog": round(float(r["HR PROGRAMADAS"]), 2),
                    "ejec": round(float(r["HRS EJECUTADAS"]), 2),
                })

    # --- Gráfico 5 (NUEVO): Matriz de Criticidad MTBF vs MTTR ---
    # ÚNICA FUENTE DE VERDAD: se construye de `kpis_hibridos` (oficial + fallback
    # CLIENTE), NO de df_kpis directo — así la matriz incluye equipos sin fila en la
    # hoja KPIs (ej. CV-00367) con el MISMO valor que muestra la tabla principal.
    # Se excluyen únicamente los equipos sin ningún dato utilizable (ni oficial ni
    # fallback calculable).
    df_matrix = pd.DataFrame([
        {
            "COD EQUIPO": eq,
            "MTBF": datos["mtbf"],
            "MTTR": datos["mttr"],
            "Cantidad de Fallas": datos["fallas"],
            "Estado": "Cumple Meta" if (datos["dm"] is not None and datos["dm"] >= datos["dm_meta"]) else "Crítico",
        }
        for eq, datos in kpis_hibridos.items()
        if datos["mtbf"] is not None and datos["mttr"] is not None and datos["fallas"] is not None
    ])
    fig_matrix = px.scatter(
        df_matrix,
        x="MTBF", y="MTTR",
        size="Cantidad de Fallas",
        color="Estado",
        color_discrete_map={"Cumple Meta": COLOR_OK, "Crítico": COLOR_CRITICAL},
        text="COD EQUIPO",
        size_max=42,
        title="<b>Matriz de Criticidad — MTBF vs. MTTR (tamaño = N° Fallas)</b>",
        hover_data={"COD EQUIPO": True, "MTBF": ':.1f', "MTTR": ':.1f', "Cantidad de Fallas": True, "Estado": False}
    )
    mtbf_mediana = df_matrix["MTBF"].median() if len(df_matrix) else 0
    mttr_mediana = df_matrix["MTTR"].median() if len(df_matrix) else 0
    fig_matrix.add_vline(x=mtbf_mediana, line_dash="dot", line_color="rgba(148,163,184,0.5)")
    fig_matrix.add_hline(y=mttr_mediana, line_dash="dot", line_color="rgba(148,163,184,0.5)")
    fig_matrix.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="#0d1b2e")))

    x_max = df_matrix["MTBF"].max() * 1.05 if len(df_matrix) else 1
    y_max = df_matrix["MTTR"].max() * 1.15 if len(df_matrix) else 1
    fig_matrix.add_annotation(x=mtbf_mediana / 2, y=y_max, text="⚠️ ALTAMENTE CRÍTICOS<br><span style='font-size:10px'>Bajo MTBF / Alto MTTR</span>",
                               showarrow=False, font=dict(color=COLOR_CRITICAL, size=12), align="center", yanchor="top")
    fig_matrix.add_annotation(x=x_max, y=y_max, text="🔶 VIGILAR<br><span style='font-size:10px'>Alto MTBF / Alto MTTR</span>",
                               showarrow=False, font=dict(color=COLOR_WARNING, size=12), align="center", yanchor="top", xanchor="right")
    fig_matrix.add_annotation(x=mtbf_mediana / 2, y=0, text="🔷 REVISAR FRECUENCIA<br><span style='font-size:10px'>Bajo MTBF / Bajo MTTR</span>",
                               showarrow=False, font=dict(color=COLOR_ACCENT_BLUE, size=12), align="center", yanchor="bottom")
    fig_matrix.add_annotation(x=x_max, y=0, text="✅ CLASE MUNDIAL<br><span style='font-size:10px'>Alto MTBF / Bajo MTTR</span>",
                               showarrow=False, font=dict(color=COLOR_OK, size=12), align="center", yanchor="bottom", xanchor="right")

    fig_matrix.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, Segoe UI, sans-serif", color="#e2e8f0"),
        hoverlabel=dict(bgcolor="rgba(21,28,44,0.95)", bordercolor="#38bdf8", font=dict(family="JetBrains Mono, monospace", size=12, color="#f8fafc")),
        xaxis=dict(title="MTBF (h) — mayor es mejor", gridcolor="rgba(148,163,184,0.12)"),
        yaxis=dict(title="MTTR (h) — menor es mejor", gridcolor="rgba(148,163,184,0.12)"),
        height=500,
        margin=dict(l=10, r=10, t=60, b=10)
    )

    # La Matriz de Criticidad tiene filtros PROPIOS de Fecha/Flota (independientes de
    # KPIS SUPERIORES). A diferencia de versiones anteriores, los valores MTBF/MTTR/
    # Fallas graficados YA NO salen de una lista precalculada en Python: se recalculan
    # 100% en vivo en JS con `calcularKpisDinamico` (la misma función que usa la tabla
    # principal, el Velocímetro y las tarjetas KPI — fuente única de verdad), para el
    # rango que el usuario elija en esta matriz. Solo las medianas (líneas punteadas de
    # cuadrante) y el layout base quedan fijos, capturados tal cual en
    # MATRIZ_MEDIANAS/MATRIX_LAYOUT_BASE — son una referencia de benchmark, no un KPI.
    matrix_medianas = {"mtbf": round(float(mtbf_mediana), 2), "mttr": round(float(mttr_mediana), 2)}

    # --- Gráfico 6 (REDISEÑADO v6): Gauge Neón Minimalista de DM Global ---
    dm_global_val = kpis_glob["dm_global"]
    meta_ref = float(df_kpis["DM GARANTIZADA"].mean() * 100) if len(df_kpis) else 88.0

    if dm_global_val >= meta_ref:
        color_anillo = COLOR_OK
    elif dm_global_val >= 85:
        color_anillo = COLOR_ACCENT_BLUE
    else:
        color_anillo = COLOR_CRITICAL

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dm_global_val,
        number={'suffix': "%", 'font': {'size': 46, 'color': '#f8fafc', 'family': 'Plus Jakarta Sans'}},
        delta={'reference': meta_ref, 'increasing': {'color': COLOR_OK}, 'decreasing': {'color': COLOR_CRITICAL},
               'font': {'size': 14}},
        title={'text': "<b>DM GLOBAL DE FLOTA</b><br><span style='font-size:11px;color:#94a3b8'>vs. Meta Contractual</span>",
               'font': {'size': 15, 'color': '#e2e8f0'}},
        gauge={
            # Anillo ultrafino: track neutro translúcido + barra de valor neón, sin bloques de color sólidos
            'axis': {'range': [0, 100], 'tickcolor': "rgba(148,163,184,0.4)", 'tickwidth': 1,
                      'tickfont': {'size': 10, 'color': '#64748b'}},
            'bar': {'color': color_anillo, 'thickness': 0.16},
            'bgcolor': "rgba(255,255,255,0.03)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': 'rgba(148,163,184,0.06)'},
            ],
            'threshold': {
                'line': {'color': COLOR_ACCENT_ORANGE, 'width': 3},
                'thickness': 0.9,
                'value': meta_ref
            }
        }
    ))
    fig_gauge.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, Segoe UI, sans-serif", color="#e2e8f0"),
        hoverlabel=dict(bgcolor="rgba(21,28,44,0.95)", bordercolor="#38bdf8", font=dict(family="JetBrains Mono, monospace", size=12, color="#f8fafc")),
        height=300,
        margin=dict(l=30, r=30, t=70, b=10)
    )

    # El Velocímetro ya NO tiene filtro local propio: su layout base (colores de fondo,
    # tipografía, título, márgenes) se captura tal cual en GAUGE_LAYOUT_BASE y se
    # reutiliza sin cambios; la traza 'indicator' (value/delta/gauge.bar/threshold) se
    # reconstruye en JS con los MISMOS dmProm/metaProm/n que ya calcula
    # `recalcularKPIsGlobales` para las tarjetas KPI superiores — un solo cálculo, dos
    # visualizaciones sincronizadas automáticamente por los filtros globales.

    # --- Gráfico 7 (v7 — JS-driven): Donut de Distribución de Inoperatividad por Sistema,
    # con filtro local de semana. La paleta se fija por identidad de sistema (no por
    # posición/ranking) a partir del ranking GLOBAL (todas las semanas), para que un
    # sistema conserve siempre el mismo color sin importar la semana filtrada.
    paleta_donut = [COLOR_CRITICAL, COLOR_ACCENT_ORANGE, COLOR_WARNING, COLOR_ACCENT_BLUE, COLOR_OK, "#a78bfa", COLOR_MUTED]
    sistemas_top6_donut = list(df_pareto["SISTEMA"].head(6)) if len(df_pareto) else []
    color_por_sistema_donut = {sist: paleta_donut[i] for i, sist in enumerate(sistemas_top6_donut)}
    color_por_sistema_donut["OTROS"] = COLOR_MUTED

    matriz_semana_sistema = calcular_matriz_semana_sistema(df_int)
    semanas_donut = sorted(int(s) for s in matriz_semana_sistema.keys() if s != "ALL")

    opciones_semanas_donut_html = '<option value="ALL" selected>Todas las Semanas</option>'
    for sem in semanas_donut:
        opciones_semanas_donut_html += f'<option value="{sem}">Semana {sem}</option>'

    # --- Gráfico 8 (NUEVO): Trendline Cumplimiento PM y Desviación por Semana ---
    df_trend_pm = calcular_resumen_horas_pm_semanal(df_plan)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=df_trend_pm["SEMANA"], y=df_trend_pm["Horas_Programadas"], name="Horas Programadas",
        marker_color=COLOR_MUTED, opacity=0.75,
        hovertemplate="Semana %{x}<br>Programadas: %{y:.1f} h<extra></extra>"
    ))
    fig_trend.add_trace(go.Bar(
        x=df_trend_pm["SEMANA"], y=df_trend_pm["Horas_Ejecutadas"], name="Horas Ejecutadas",
        marker_color=COLOR_ACCENT_BLUE,
        hovertemplate="Semana %{x}<br>Ejecutadas: %{y:.1f} h<extra></extra>"
    ))
    fig_trend.add_trace(go.Scatter(
        x=df_trend_pm["SEMANA"], y=df_trend_pm["Pct_Cumplimiento"], name="% Cumplimiento PM",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLOR_OK, width=3),
        marker=dict(size=9, color=COLOR_OK, line=dict(width=1, color="#fff")),
        hovertemplate="Semana %{x}<br>Cumplimiento: %{y:.1f}%<extra></extra>"
    ))
    fig_trend.update_layout(
        title="<b>Tendencia de Cumplimiento PM — Programado vs. Ejecutado por Semana</b>",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, Segoe UI, sans-serif", color="#e2e8f0"),
        hoverlabel=dict(bgcolor="rgba(21,28,44,0.95)", bordercolor="#38bdf8", font=dict(family="JetBrains Mono, monospace", size=12, color="#f8fafc")),
        xaxis=dict(title="Semana", gridcolor="rgba(148,163,184,0.1)", dtick=1),
        yaxis=dict(title="Horas", gridcolor="rgba(148,163,184,0.12)"),
        yaxis2=dict(title="% Cumplimiento", overlaying="y", side="right", range=[0, 110], showgrid=False),
        hovermode="x unified",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60, b=10)
    )

    # Generación de Fragmentos HTML (fig_dm, fig_pareto y fig_otros son JS-driven, ver más abajo)
    html_fig_pm = fig_pm.to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False}, div_id="chartPMDesviacion")
    html_fig_matrix = fig_matrix.to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False}, div_id="chartMatrixCriticidad")
    html_fig_gauge = fig_gauge.to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False}, div_id="chartGaugeDM")
    html_fig_trend = fig_trend.to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False}, div_id="chartTrendPM")

    # --- Micro-indicadores de tendencia para las tarjetas KPI superiores ---
    delta_dm_vs_meta = kpis_glob["dm_global"] - meta_ref
    trend_dm_class = "kpi-trend-up" if delta_dm_vs_meta >= 0 else "kpi-trend-down"
    trend_dm_icon = "fa-arrow-trend-up" if delta_dm_vs_meta >= 0 else "fa-arrow-trend-down"
    trend_dm_html = f'<span class="kpi-trend {trend_dm_class}"><i class="fa-solid {trend_dm_icon}"></i> {delta_dm_vs_meta:+.1f} pp vs meta</span>'

    delta_mtbf_vs_mediana = kpis_glob["mtbf_global"] - mtbf_mediana
    trend_mtbf_class = "kpi-trend-up" if delta_mtbf_vs_mediana >= 0 else "kpi-trend-down"
    trend_mtbf_icon = "fa-arrow-trend-up" if delta_mtbf_vs_mediana >= 0 else "fa-arrow-trend-down"
    trend_mtbf_html = f'<span class="kpi-trend {trend_mtbf_class}"><i class="fa-solid {trend_mtbf_icon}"></i> {delta_mtbf_vs_mediana:+.1f} h vs mediana flota</span>'

    delta_mttr_vs_mediana = kpis_glob["mttr_global"] - mttr_mediana
    # Para MTTR, menor es mejor: si está por debajo de la mediana, es una tendencia positiva.
    trend_mttr_class = "kpi-trend-up" if delta_mttr_vs_mediana <= 0 else "kpi-trend-down"
    trend_mttr_icon = "fa-arrow-trend-down" if delta_mttr_vs_mediana <= 0 else "fa-arrow-trend-up"
    trend_mttr_html = f'<span class="kpi-trend {trend_mttr_class}"><i class="fa-solid {trend_mttr_icon}"></i> {delta_mttr_vs_mediana:+.1f} h vs mediana flota</span>'

    def generar_sparkline_svg(valores: list, color: str, width: int = 100, height: int = 28) -> str:
        """Sparkline SVG minimalista para tendencias semanales dentro de las tarjetas KPI."""
        if not valores or len(valores) < 2:
            return '<span style="font-size:0.68rem;color:#64748b;">Sin histórico semanal suficiente</span>'

        v_min, v_max = min(valores), max(valores)
        rango = (v_max - v_min) or 1
        n = len(valores)
        pad = 3
        puntos = []
        for idx, v in enumerate(valores):
            x = pad + (idx / (n - 1)) * (width - 2 * pad)
            y = height - pad - ((v - v_min) / rango) * (height - 2 * pad)
            puntos.append(f"{x:.1f},{y:.1f}")
        puntos_str = " ".join(puntos)
        ultimo_x, ultimo_y = puntos[-1].split(",")

        return f'''<svg class="kpi-sparkline" width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <polyline points="{puntos_str}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" />
            <circle cx="{ultimo_x}" cy="{ultimo_y}" r="2.6" fill="{color}" />
        </svg>'''

    sparkline_dm_html = generar_sparkline_svg(tendencia_dm_serie, COLOR_ACCENT_BLUE)
    sparkline_fallas_html = generar_sparkline_svg(tendencia_fallas_serie, COLOR_CRITICAL)

    opciones_semanas_html = ""
    for sem in semanas:
        selected = "selected" if str(sem) == ultima_semana else ""
        opciones_semanas_html += f'<option value="{sem}" {selected}>Semana {sem}</option>'

    fecha_min = df_int["FECHA"].min()
    fecha_max = df_int["FECHA"].max()
    str_fmin = fecha_min.strftime("%Y-%m-%d") if pd.notnull(fecha_min) else "2026-07-01"
    str_fmax = fecha_max.strftime("%Y-%m-%d") if pd.notnull(fecha_max) else "2026-07-10"

    # Catálogo de equipos para el frontend — se arma directo de `kpis_hibridos` (ÚNICA
    # fuente de verdad calculada arriba); no se vuelve a leer df_kpis ni a invocar el
    # fallback aquí, para no duplicar cálculo ni arriesgar una divergencia con la
    # Matriz de Criticidad, que usa el mismo `kpis_hibridos`.
    catalogo_equipos = []
    lista_equipos_unicos = sorted(df_parque["COD INTERNO"].unique())
    opciones_equipos_html = '<option value="ALL">Todos los equipos</option>'

    for eq in lista_equipos_unicos:
        hibrido = kpis_hibridos.get(eq, {})
        catalogo_equipos.append({
            "equipo": eq,
            "contrato_gold": hibrido.get("contrato_gold", "NO ESPECIFICADO"),
            "categoria": hibrido.get("categoria", "CLIENTE"),
            "dm_meta": hibrido.get("dm_meta", 88.0),
            "dm_oficial": hibrido.get("dm"),
            "mtbf_oficial": hibrido.get("mtbf"),
            "mttr_oficial": hibrido.get("mttr"),
            "fallas_oficial": hibrido.get("fallas"),
            "horas_inoperativas": hibrido.get("horas_inoperativas"),
            "es_calculo_dinamico": hibrido.get("es_calculo_dinamico", False),
            "falla_en_curso": hibrido.get("falla_en_curso", False),
            "dias_sin_falla": dias_sin_falla_dict.get(eq),
        })
        opciones_equipos_html += f'<option value="{eq}">{eq}</option>'

    raw_intervenciones = preparar_raw_intervenciones_js(df_int)

    json_pm_semanas = json.dumps(data_pm_semanas)
    json_catalogo = json.dumps(catalogo_equipos)
    json_raw_intervenciones = json.dumps(raw_intervenciones)
    # Orden exacto de semanas con el que se construyeron las trazas de fig_pm (2 por semana:
    # Hrs Programadas / Hrs Ejecutadas), para que el selector de la tarjeta KPI pueda
    # sincronizar la visibilidad de trazas en JS sin duplicar la lógica de cálculo de Python.
    json_semanas_pm_chart = json.dumps([int(s) for s in semanas])

    # Datos + paleta del gráfico "Obras/Otras Actividades" (Programado vs. Ejecutado
    # por Tipo de Actividad, JS-driven "Dashboard Executive Premium").
    json_otros_data = json.dumps(otros_data_list)
    json_pares_color_actividad = json.dumps(pares_color_actividad)
    json_tipos_actividad_orden = json.dumps(list(tipos_actividad))

    # Matriz [Semana][Sistema] -> Horas de Inoperatividad + paleta fija por sistema,
    # para el filtro local de semana del donut de Inoperatividad por Sistema.
    json_matriz_semana_sistema = json.dumps(matriz_semana_sistema)
    json_donut_color_map = json.dumps(color_por_sistema_donut)
    json_donut_top6 = json.dumps(sistemas_top6_donut)

    # Matriz de Criticidad MTBF/MTTR: medianas + el layout EXACTO ya calculado por
    # Python (ejes, líneas punteadas y anotaciones de los 4 cuadrantes) — se reutiliza
    # sin cambios en el render JS. Los puntos en sí se calculan en vivo (ver arriba).
    json_matrix_medianas = json.dumps(matrix_medianas)
    json_matrix_layout_base = json.dumps(fig_matrix.to_plotly_json()["layout"], cls=PlotlyJSONEncoder)

    # Layout EXACTO del velocímetro (colores de fondo, título, márgenes) — se reutiliza
    # sin cambios en cada re-render JS; solo cambia la traza 'indicator', reconstruida
    # con los mismos dmProm/metaProm/n de `recalcularKPIsGlobales` (sin filtro propio).
    json_gauge_layout_base = json.dumps(fig_gauge.to_plotly_json()["layout"], cls=PlotlyJSONEncoder)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Confiabilidad | STRACON — Antamina | Volvo FMX D13C 540HP</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>
        <style>
            :root {{
                --bg-deep: {COLOR_BG_DEEP};
                --panel: {COLOR_PANEL};
                --orange: {COLOR_ACCENT_ORANGE};
                --blue: {COLOR_ACCENT_BLUE};
                --ok: {COLOR_OK};
                --critical: {COLOR_CRITICAL};
                --warning: {COLOR_WARNING};
                --muted: {COLOR_MUTED};
                --violet: {COLOR_VIOLET};
                --cyan: {COLOR_CYAN};
            }}
            * {{ box-sizing: border-box; }}
            body {{
                background: radial-gradient(circle at 12% 0%, #101c33 0%, var(--bg-deep) 55%);
                color: #e5e7eb;
                font-family: 'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif;
                padding-bottom: 60px;
                min-height: 100vh;
                letter-spacing: 0.01em;
            }}
            .navbar {{
                background: rgba(9, 13, 22, 0.8);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border-bottom: 1px solid rgba(247, 147, 30, 0.22);
                box-shadow: 0 4px 30px rgba(0,0,0,0.45);
            }}
            .navbar-brand {{ font-weight: 800; letter-spacing: 0.01em; }}
            .glass-panel {{
                background: rgba(17, 24, 39, 0.62);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            }}
            .kpi-card {{
                background: linear-gradient(135deg, rgba(30,41,59,0.6) 0%, rgba(17,24,39,0.7) 100%);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 20px;
                position: relative;
                overflow: hidden;
                transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            }}
            .kpi-card::before {{
                content: '';
                position: absolute; inset: 0; border-radius: 16px; padding: 1px;
                background: linear-gradient(135deg, rgba(56,189,248,0.35), rgba(247,147,30,0.15) 60%, transparent);
                -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor; mask-composite: exclude;
                opacity: 0; transition: opacity 0.25s ease;
                pointer-events: none;
            }}
            .kpi-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 12px 44px rgba(56, 189, 248, 0.22), 0 0 0 1px rgba(56,189,248,0.08) inset;
                border-color: rgba(56, 189, 248, 0.45);
            }}
            .kpi-card:hover::before {{ opacity: 1; }}
            .kpi-icon {{
                position: absolute; right: 14px; top: 14px; font-size: 1.6rem; opacity: 0.18;
                transition: opacity 0.25s ease, transform 0.25s ease;
            }}
            .kpi-card:hover .kpi-icon {{ opacity: 0.4; transform: scale(1.15) rotate(-6deg); }}
            .kpi-title {{ font-size: 0.78rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.06em; font-weight: 700; }}
            .kpi-value {{ font-size: 2.6rem; font-weight: 800; margin-top: 6px; line-height: 1; text-shadow: 0 0 20px currentColor; opacity: 0.97; letter-spacing: -0.02em; }}
            .kpi-trend {{
                display: inline-flex; align-items: center; gap: 4px; font-size: 0.72rem; font-weight: 700;
                padding: 2px 8px; border-radius: 999px; margin-top: 6px; letter-spacing: 0.02em;
            }}
            .kpi-trend-up {{ background: rgba(16,185,129,0.14); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }}
            .kpi-trend-down {{ background: rgba(220,38,38,0.14); color: #f87171; border: 1px solid rgba(220,38,38,0.4); }}
            .kpi-trend-warn {{ background: rgba(245,158,11,0.14); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4); }}
            /* --- Barra de filtros + badges de contexto del bloque KPI superior --- */
            .kpi-filter-bar {{
                display: flex; align-items: center; flex-wrap: wrap; gap: 10px;
                background: rgba(9,13,22,0.55); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px; padding: 10px 16px; margin-bottom: 12px;
            }}
            .kpi-filter-bar-label {{ font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
            .gauge-badges-row {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; margin-top: -4px; padding-bottom: 6px; }}
            .gauge-badge-neutral {{ background: rgba(56,189,248,0.12); color: var(--blue); border: 1px solid rgba(56,189,248,0.4); }}

            /* --- Ficha Técnica Volvo FMX (paleta Cyber-Industrial propia de esta sección) --- */
            .tech-banner {{
                background: #0d1117; border: 1px solid rgba(0,180,216,0.25); border-radius: 16px;
                padding: 18px 22px; margin-top: 18px;
                box-shadow: 0 0 0 1px rgba(0,180,216,0.05), 0 8px 28px rgba(0,0,0,0.35);
            }}
            .tech-banner-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
            .tech-banner-header i {{ font-size: 1.6rem; color: #ffd166; }}
            .tech-banner-title {{ font-size: 0.95rem; font-weight: 800; letter-spacing: 0.03em; color: #00b4d8; }}
            .tech-banner-subtitle {{ font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }}
            .tech-banner-body {{ display: flex; flex-wrap: wrap; align-items: center; gap: 22px; }}
            .tech-img-wrap {{ flex: 1 1 480px; min-width: 320px; display: flex; justify-content: center; }}
            .tech-img-fallback {{
                display: flex; align-items: center; justify-content: center; gap: 8px;
                width: 100%; max-width: 650px; min-height: 200px; color: #64748b;
                font-size: 0.85rem; border: 1px dashed rgba(0,180,216,0.3); border-radius: 8px;
            }}
            .tech-spec-grid {{ flex: 1 1 360px; display: flex; flex-direction: column; gap: 10px; min-width: 300px; }}
            .tech-spec-card {{
                display: flex; align-items: flex-start; gap: 10px;
                background: rgba(0,180,216,0.05); border: 1px solid rgba(0,180,216,0.18);
                border-radius: 10px; padding: 9px 12px;
            }}
            .tech-spec-num {{
                flex: none; width: 24px; height: 24px; border-radius: 50%;
                background: #0d1117; border: 2px solid #ffd166; color: #ffd166;
                font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.75rem;
                display: flex; align-items: center; justify-content: center;
            }}
            .tech-spec-title {{ font-size: 0.78rem; font-weight: 800; color: #00b4d8; letter-spacing: 0.02em; }}
            .tech-spec-detail {{ font-size: 0.72rem; color: #cbd5e1; margin-top: 2px; }}
            .kpi-sub {{ font-size: 0.75rem; color: #94a3b8; margin-top: 4px; }}
            .chart-card {{ margin-top: 20px; padding: 15px; }}

            /* Badges de estado — glow neón */
            .badge-ok {{ background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid var(--ok); box-shadow: 0 0 14px rgba(16,185,129,0.35); font-weight: 700; letter-spacing: 0.03em; }}
            .badge-danger {{ background-color: rgba(220, 38, 38, 0.15); color: #f87171; border: 1px solid var(--critical); box-shadow: 0 0 14px rgba(220,38,38,0.4); font-weight: 700; letter-spacing: 0.03em; }}
            .badge-offender {{ background: linear-gradient(90deg, var(--critical), var(--orange)); color: #fff; border: none; font-weight: 700; box-shadow: 0 0 14px rgba(247,147,30,0.35); animation: pulseGlow 2.2s ease-in-out infinite; }}
            @keyframes pulseGlow {{
                0%, 100% {{ box-shadow: 0 0 10px rgba(247,147,30,0.25); }}
                50% {{ box-shadow: 0 0 20px rgba(220,38,38,0.5); }}
            }}
            .badge-alert {{ background: var(--critical); color: #fff; border: none; font-weight: 700; animation: pulseAlert 1.3s ease-in-out infinite; }}
            /* --- Módulo independiente MTBS (namespace mtbs*, sin acoplar a otras tarjetas) --- */
            .mtbs-badge-modulo {{
                background: rgba(167,139,250,0.14); color: var(--violet); border: 1px solid rgba(167,139,250,0.5);
                font-size: 0.62rem; font-weight: 700; letter-spacing: 0.04em; vertical-align: middle;
            }}
            /* --- Módulo independiente Backlog (namespace bkl*, sin acoplar a otras tarjetas) --- */
            .bkl-badge-modulo {{
                background: rgba(34,211,238,0.14); color: var(--cyan); border: 1px solid rgba(34,211,238,0.5);
                font-size: 0.62rem; font-weight: 700; letter-spacing: 0.04em; vertical-align: middle;
            }}
            @keyframes pulseAlert {{
                0%, 100% {{ box-shadow: 0 0 6px rgba(220,38,38,0.4); }}
                50% {{ box-shadow: 0 0 16px rgba(220,38,38,0.9); }}
            }}
            .brecha-neg {{ color: #ff6b6b; font-weight: 800; text-shadow: 0 0 10px rgba(255,107,107,0.5); }}
            .brecha-pos {{ color: #34d399; font-weight: 700; }}

            /* Pastillas de categoría diferenciadas */
            .pill-categoria {{
                display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: 0.7rem;
                font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap;
            }}
            .pill-cliente {{ background: rgba(34, 211, 238, 0.14); color: var(--cyan); border: 1px solid rgba(34,211,238,0.5); box-shadow: 0 0 10px rgba(34,211,238,0.2); }}
            .pill-contrato {{ background: rgba(167, 139, 250, 0.14); color: var(--violet); border: 1px solid rgba(167,139,250,0.5); box-shadow: 0 0 10px rgba(167,139,250,0.2); }}
            .pill-alquilados {{ background: rgba(245, 158, 11, 0.14); color: var(--warning); border: 1px solid rgba(245,158,11,0.5); box-shadow: 0 0 10px rgba(245,158,11,0.2); }}

            /* --- TABLA: corrección estricta de legibilidad --- */
            .table-wrapper {{ max-height: 620px; overflow-y: auto; overflow-x: auto; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); }}
            .chart-scroll-x {{ overflow-x: auto; overflow-y: hidden; }}
            /* --- "Dashboard Executive Premium": profundidad/glow para Obras/Otras Actividades --- */
            .chart-otros-premium {{
                filter: drop-shadow(0 6px 14px rgba(167,139,250,0.28)) drop-shadow(0 2px 4px rgba(0,0,0,0.4));
            }}
            table.table-custom {{ color: #e5e7eb; background-color: transparent; margin-bottom: 0; border-collapse: separate; border-spacing: 0; min-width: 900px; }}
            .table-custom thead th {{
                position: sticky; top: 0; z-index: 5;
                background-color: #0f172a; color: #94a3b8;
                border-bottom: 2px solid rgba(255,255,255,0.1);
                font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;
                padding: 12px 14px; cursor: pointer; user-select: none; white-space: nowrap;
            }}
            .table-custom thead th:hover {{ color: var(--blue); }}
            .table-custom thead th .sort-icon {{ font-size: 0.65rem; opacity: 0.5; margin-left: 4px; }}
            .table-custom td {{ border-bottom: 1px solid rgba(255,255,255,0.06); vertical-align: middle; padding: 10px 14px; }}
            .table-custom tbody tr {{ transition: background-color 0.15s ease; }}
            .table-custom tbody tr:hover {{ background-color: rgba(56, 189, 248, 0.07); }}
            .row-critical {{ background-color: rgba(220, 38, 38, 0.08); }}
            .row-critical:hover {{ background-color: rgba(220, 38, 38, 0.14) !important; }}
            .col-equipo {{
                color: #ffffff !important; font-weight: 700; min-width: 170px; white-space: nowrap;
            }}
            .dm-cell {{ min-width: 140px; }}
            .dm-bar-track {{
                width: 100%; height: 7px; border-radius: 4px; background: rgba(255,255,255,0.08);
                margin-top: 5px; overflow: hidden;
            }}
            .dm-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.4s ease; }}

            .input-kpi, .select-kpi {{
                background-color: rgba(9,13,22,0.75); color: var(--blue);
                border: 1px solid rgba(255,255,255,0.12); border-radius: 8px;
                font-size: 0.85rem; padding: 5px 10px; outline: none;
                font-weight: 600; transition: all 0.2s ease;
            }}
            .input-kpi:focus, .select-kpi:focus {{ border-color: var(--blue); box-shadow: 0 0 0 3px rgba(56,189,248,0.15); }}
            #buscadorEquipo {{ min-width: 220px; }}
            #buscadorEquipo::placeholder {{ color: #64748b; }}
            .btn-export {{
                background: linear-gradient(90deg, var(--ok), #059669); border: none; color: #fff; font-weight: 700;
                border-radius: 8px; transition: transform 0.15s ease, box-shadow 0.15s ease;
            }}
            .btn-export:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16,185,129,0.3); color: #fff; }}
            .btn-navbar-action {{
                background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.4); color: var(--blue);
                font-weight: 700; border-radius: 8px; transition: all 0.15s ease;
            }}
            .btn-navbar-action:hover {{ background: rgba(56,189,248,0.25); color: #fff; box-shadow: 0 0 14px rgba(56,189,248,0.35); }}
            .btn-reset {{ border-radius: 8px; }}
            .section-title {{ font-weight: 800; letter-spacing: 0.01em; }}
            ::-webkit-scrollbar {{ height: 8px; width: 8px; }}
            ::-webkit-scrollbar-thumb {{ background: rgba(148,163,184,0.35); border-radius: 4px; }}

            /* --- Mini-toolbar por gráfico (Requerimiento 1) --- */
            .chart-toolbar {{
                display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
                padding-bottom: 10px; margin-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.06);
            }}
            .chart-toolbar-title {{ font-size: 0.85rem; font-weight: 700; color: #cbd5e1; }}
            .chart-toolbar-controls {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
            .select-mini {{
                background-color: rgba(9,13,22,0.75); color: var(--blue);
                border: 1px solid rgba(255,255,255,0.12); border-radius: 6px;
                font-size: 0.75rem; padding: 3px 8px; outline: none; font-weight: 600;
            }}
            .btn-fullscreen {{
                background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.35); color: var(--blue);
                border-radius: 6px; width: 28px; height: 28px; font-size: 0.75rem;
                display: inline-flex; align-items: center; justify-content: center;
                transition: all 0.2s ease; cursor: pointer;
            }}
            .btn-fullscreen:hover {{ background: rgba(56,189,248,0.25); box-shadow: 0 0 14px rgba(56,189,248,0.35); }}
            .chart-container {{ transition: all 0.25s ease; }}
            .chart-fullscreen {{
                position: fixed !important; top: 20px; left: 20px; right: 20px; bottom: 20px;
                z-index: 2000; overflow: auto; background: rgba(11,15,25,0.92) !important;
                backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
                box-shadow: 0 0 100px rgba(0,0,0,0.7), 0 0 0 1px rgba(56,189,248,0.3);
            }}
            .chart-fullscreen > div[id^="chart"] {{ height: calc(100% - 60px) !important; }}

            /* --- Chip de cross-filtering flotante (Requerimiento 2) --- */
            #chipFiltroCross {{
                position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
                z-index: 3000; background: rgba(17,24,39,0.92); backdrop-filter: blur(14px);
                border: 1px solid var(--orange); border-radius: 999px; padding: 9px 18px;
                font-size: 0.82rem; font-weight: 700; color: #f8fafc; cursor: pointer;
                box-shadow: 0 0 24px rgba(247,147,30,0.4); display: none; align-items: center; gap: 8px;
                transition: transform 0.15s ease;
            }}
            #chipFiltroCross:hover {{ transform: translateX(-50%) scale(1.04); }}
            #chipFiltroCross i {{ color: var(--orange); }}

            /* --- Corrección estricta de visibilidad EQUIPO + LED pulse (Requerimiento 3) --- */
            .badge-equipo {{
                display: inline-block; background-color: #151c2c !important; color: #f8fafc !important;
                font-weight: 700; padding: 4px 10px; border-radius: 8px;
                border: 1px solid rgba(56,189,248,0.4); box-shadow: 0 0 10px rgba(56,189,248,0.12);
                white-space: nowrap;
            }}
            .led-dot {{
                display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px;
            }}
            .led-green {{ background: var(--ok); box-shadow: 0 0 6px 2px rgba(16,185,129,0.7); animation: ledPulseGreen 1.6s ease-in-out infinite; }}
            .led-red {{ background: var(--critical); box-shadow: 0 0 6px 2px rgba(220,38,38,0.7); animation: ledPulseRed 1.1s ease-in-out infinite; }}
            @keyframes ledPulseGreen {{
                0%, 100% {{ box-shadow: 0 0 4px 1px rgba(16,185,129,0.5); opacity: 0.85; }}
                50% {{ box-shadow: 0 0 10px 4px rgba(16,185,129,0.9); opacity: 1; }}
            }}
            @keyframes ledPulseRed {{
                0%, 100% {{ box-shadow: 0 0 4px 1px rgba(220,38,38,0.5); opacity: 0.85; }}
                50% {{ box-shadow: 0 0 12px 5px rgba(220,38,38,0.95); opacity: 1; }}
            }}

            /* --- Sparklines de tendencia en tarjetas KPI (Requerimiento 4) --- */
            .kpi-sparkline {{ margin-top: 6px; opacity: 0.9; }}

            /* --- Impresión / Exportar a PDF: oculta controles interactivos --- */
            @media print {{
                .no-print, .chart-toolbar-controls, .btn-fullscreen, #chipFiltroCross {{ display: none !important; }}
                body {{ background: #fff !important; color: #111 !important; }}
                .glass-panel {{ background: #fff !important; border: 1px solid #ccc !important; box-shadow: none !important; }}
                .chart-container {{ page-break-inside: avoid; }}
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark mb-4">
            <div class="container-fluid px-4 py-2 d-flex justify-content-between align-items-center flex-wrap gap-2">
                <div>
                    <span class="navbar-brand mb-0 h1"><i class="fa-solid fa-truck-monster me-2" style="color: var(--orange);"></i> STRACON — Control de Confiabilidad | Volvo FMX — Motor D13C (540 HP)</span>
                    <div class="text-secondary small">Operación Antamina | Volvo FMX 8x4 R · Motor D13C Euro 5 (540 HP / 2600 Nm) | Generado por Vince Rivera con Python + Plotly</div>
                </div>
                <div class="navbar-actions d-flex gap-2 no-print">
                    <button class="btn btn-sm btn-navbar-action" onclick="window.print()" title="Imprimir o guardar como PDF">
                        <i class="fa-solid fa-file-pdf me-1"></i>Imprimir / PDF
                    </button>
                    <button class="btn btn-sm btn-navbar-action" onclick="exportarExcel()" title="Exportar la data filtrada de la tabla a Excel">
                        <i class="fa-solid fa-file-excel me-1"></i>Exportar Excel
                    </button>
                </div>
            </div>
        </nav>

        <div class="container-fluid px-4 pt-3">
            {banner_tecnico_html}
        </div>

        <div id="chipFiltroCross" onclick="limpiarFiltroCross()">
            <i class="fa-solid fa-filter-circle-xmark"></i>
            <span id="chipFiltroCrossTexto">Filtrando por: —</span>
            <i class="fa-solid fa-xmark ms-1"></i>
        </div>

        <div class="container-fluid px-4">
            <!-- BARRA DE FILTROS DEL BLOQUE KPI SUPERIOR (Periodo + Flota/Subflota) —
                 comparte estado con los filtros de la tabla (Semana/Fecha/Grupo) para
                 que TODO el dashboard quede consistente con una sola fuente de verdad. -->
            <div class="kpi-filter-bar">
                <span class="kpi-filter-bar-label"><i class="fa-solid fa-sliders me-1"></i>KPIs superiores:</span>

                <label class="text-secondary small fw-bold mb-0">Periodo:</label>
                <span class="text-secondary small">Seleccione fechas</span>

                <span id="grupoFechaKPI" class="d-flex align-items-center gap-2">
                    <input type="date" id="fechaInicioKPI" class="input-kpi" value="{str_fmin}" onchange="sincronizarFiltrosKPISuperiores()">
                    <span class="text-secondary small">—</span>
                    <input type="date" id="fechaFinKPI" class="input-kpi" value="{str_fmax}" onchange="sincronizarFiltrosKPISuperiores()">
                </span>

                <label class="text-secondary small fw-bold mb-0 ms-2">Flota/Subflota:</label>
                <select id="selectFlotaKPI" class="select-kpi" onchange="sincronizarFiltrosKPISuperiores()">
                    <option value="ALL" selected>Todas las flotas</option>
                    <option value="CONTRATO">Volvo FMX — Contrato / Propio</option>
                    <option value="CLIENTE">Volvo FMX — Cliente</option>
                    <option value="ALQUILADOS">Volvo FMX — Alquilado</option>
                </select>
            </div>

            <!-- METRICAS KPI (recalculables en vivo) -->
            <div class="row g-3">
                <div class="col-md-2">
                    <div class="kpi-card">
                        <i class="fa-solid fa-gauge-high kpi-icon" style="color: var(--blue);"></i>
                        <div class="kpi-title">DM Global</div>
                        <div class="kpi-value" style="color: var(--blue);" id="kpiDMGlobal">{kpis_glob['dm_global']}%</div>
                        <div class="kpi-sub" id="kpiDMGlobalSub">Flota completa</div>
                        <div>{trend_dm_html}</div>
                        <span id="sparklineDMWrap">{sparkline_dm_html}</span>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="kpi-card">
                        <i class="fa-solid fa-clock-rotate-left kpi-icon" style="color: var(--ok);"></i>
                        <div class="kpi-title">MTBF Flota</div>
                        <div class="kpi-value" style="color: var(--ok);" id="kpiMTBFGlobal">{kpis_glob['mtbf_global']} <span class="fs-6">h</span></div>
                        <div class="kpi-sub">Tiempo medio entre fallas</div>
                        <div>{trend_mtbf_html}</div>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="kpi-card">
                        <i class="fa-solid fa-wrench kpi-icon" style="color: var(--warning);"></i>
                        <div class="kpi-title">MTTR Flota</div>
                        <div class="kpi-value" style="color: var(--warning);" id="kpiMTTRGlobal">{kpis_glob['mttr_global']} <span class="fs-6">h</span></div>
                        <div class="kpi-sub">Tiempo medio de reparación</div>
                        <div>{trend_mttr_html}</div>
                    </div>
                </div>

                <div class="col-md-3">
                    <div class="kpi-card">
                        <i class="fa-solid fa-calendar-check kpi-icon" style="color: var(--blue);"></i>
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="kpi-title">Cumplimiento PM</div>
                            <select id="selectSemanaPM" class="select-kpi" onchange="actualizarKpiPM(this.value)">
                                {opciones_semanas_html}
                            </select>
                        </div>
                        <div class="kpi-value" style="color: var(--blue);" id="kpiValuePM">{datos_ultima_sem['pct']}%</div>
                        <small class="kpi-sub" id="kpiDetailPM">{datos_ultima_sem['ejecutados']} de {datos_ultima_sem['programados']} ejecutados</small>
                        <div id="kpiEstadoPM"></div>
                    </div>
                </div>

                <div class="col-md-3">
                    <div class="kpi-card">
                        <i class="fa-solid fa-triangle-exclamation kpi-icon" style="color: var(--critical);"></i>
                        <div class="kpi-title">Unidades Bajo Meta</div>
                        <div class="kpi-value" style="color: var(--critical);" id="kpiFueraMeta">{kpis_glob['fuera_meta']} <span class="fs-6">equipos</span></div>
                        <div class="kpi-sub" id="kpiFallasGlobal">{kpis_glob['total_fallas']} fallas registradas</div>
                        {sparkline_fallas_html}
                    </div>
                </div>
            </div>

            <!-- GAUGE DM GLOBAL + ESTADO DE FLOTA DEL DÍA -->
            <div class="row mt-2">
                <div class="col-lg-5">
                    <div class="glass-panel chart-card chart-container h-100" id="panel_gauge">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-gauge-high me-1"></i>Velocímetro DM Global</span>
                            <div class="chart-toolbar-controls">
                                <span class="text-secondary small" title="Reacciona automáticamente a los filtros de KPIS SUPERIORES (Periodo / Flota)">
                                    <i class="fa-solid fa-link me-1"></i>Sincronizado con KPIs superiores
                                </span>
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_gauge')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        {html_fig_gauge}
                        <div class="gauge-badges-row">
                            <span class="kpi-trend gauge-badge-neutral" id="gaugeMetaBadge">Meta Contractual: —</span>
                            <span class="kpi-trend kpi-trend-up" id="gaugeBrechaBadge">Brecha / Desviación: —</span>
                            <span class="kpi-trend gauge-badge-neutral" id="gaugeUnidadesBadge">Unidades Evaluadas: —</span>
                        </div>
                    </div>
                </div>
                <div class="col-lg-7">
                    {efd_panel_html}
                </div>
            </div>

            <!-- FILA GRÁFICOS PRINCIPALES (JS-driven: DM y Pareto con mini-toolbar local) -->
            <div class="row mt-2">
                <div class="col-lg-6">
                    <div class="glass-panel chart-card chart-container" id="panel_dm">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-chart-bar me-1"></i>Disponibilidad Mecánica vs. Meta</span>
                            <div class="chart-toolbar-controls">
                                <select class="select-mini" id="selectTopNDM" onchange="aplicarFiltrosTabla('topn-dm')">
                                    <option value="5">Top 5 peor DM</option>
                                    <option value="10" selected>Top 10 peor DM</option>
                                    <option value="ALL">Todos</option>
                                </select>
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_dm')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        <div id="chartDM" style="width:100%; height:460px;"></div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="glass-panel chart-card chart-container" id="panel_pareto">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-ranking-star me-1"></i>Pareto de Sistemas Críticos</span>
                            <div class="chart-toolbar-controls">
                                <select class="select-mini" id="selectMetricaPareto" onchange="aplicarFiltrosTabla('metrica-pareto')">
                                    <option value="horas" selected>Horas Parada</option>
                                    <option value="eventos">N° de Eventos</option>
                                    <option value="mttr">MTTR</option>
                                </select>
                                <select class="select-mini" id="selectTopNPareto" onchange="aplicarFiltrosTabla('topn-pareto')">
                                    <option value="5">Top 5</option>
                                    <option value="10" selected>Top 10</option>
                                    <option value="crit10">Top 10 Criticidad</option>
                                    <option value="ALL">Todos</option>
                                </select>
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_pareto')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        <div id="chartPareto" style="width:100%; height:460px;"></div>
                    </div>
                </div>
            </div>

            <!-- MATRIZ DE CRITICIDAD -->
            <div class="row mt-2">
                <div class="col-12">
                    <div class="glass-panel chart-card chart-container" id="panel_matrix">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-braille me-1"></i>Matriz de Criticidad MTBF vs. MTTR</span>
                            <div class="chart-toolbar-controls">
                                <select class="select-mini" id="matrixSelectFlota" onchange="renderMatrixChart()" title="Filtro propio de esta matriz — independiente de KPIS SUPERIORES">
                                    <option value="ALL" selected>Todos</option>
                                    <option value="CONTRATO">Contrato</option>
                                    <option value="CLIENTE">Cliente</option>
                                </select>
                                <input type="date" id="matrixFechaInicio" class="input-kpi" value="{str_fmin}" onchange="renderMatrixChart()" title="Fecha Inicio (propia de esta matriz)">
                                <span class="text-secondary small">—</span>
                                <input type="date" id="matrixFechaFin" class="input-kpi" value="{str_fmax}" onchange="renderMatrixChart()" title="Fecha Fin (propia de esta matriz)">
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_matrix')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        {html_fig_matrix}
                    </div>
                </div>
            </div>

            <!-- DONUT INOPERATIVIDAD POR SISTEMA -->
            <div class="row mt-2">
                <div class="col-lg-5">
                    <div class="glass-panel chart-card chart-container" id="panel_donut">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-circle-notch me-1"></i>Inoperatividad por Sistema</span>
                            <div class="chart-toolbar-controls">
                                <select class="select-mini" id="selectSemanaDonut" onchange="renderDonutChart(this.value)">
                                    {opciones_semanas_donut_html}
                                </select>
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_donut')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        <div id="chartDonut" style="width:100%; height:420px;"></div>
                    </div>
                </div>
                <div class="col-lg-7">
                    <div class="glass-panel chart-card chart-container" id="panel_trend">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-arrow-trend-up me-1"></i>Tendencia Cumplimiento PM Semanal</span>
                            <button class="btn-fullscreen" onclick="toggleFullscreen('panel_trend')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                        </div>
                        {html_fig_trend}
                    </div>
                </div>
            </div>

            <!-- GRÁFICO PM PREVENTIVO -->
            <div class="row mt-2">
                <div class="col-12">
                    <div class="glass-panel chart-card chart-container" id="panel_pm">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-screwdriver-wrench me-1"></i>Desviación Mantenimiento Preventivo</span>
                            <button class="btn-fullscreen" onclick="toggleFullscreen('panel_pm')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                        </div>
                        {html_fig_pm}
                    </div>
                </div>
            </div>

            <!-- GRÁFICO OTRAS ACTIVIDADES -->
            <div class="row mt-2">
                <div class="col-12">
                    <div class="glass-panel chart-card chart-container" id="panel_otros">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-helmet-safety me-1"></i>Programado vs. Ejecutado — Obras/Otras Actividades</span>
                            <div class="chart-toolbar-controls">
                                <select class="select-mini" id="selectSemanaOtros" onchange="renderOtrosChart(this.value)">
                                    {opciones_semanas_html}
                                </select>
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_otros')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        <div class="chart-otros-premium chart-scroll-x">
                            <div id="chartOtrosWrap" style="min-width:900px;">
                                <div id="chartOtrosActividades" style="width:100%; height:520px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TABLA DE DETALLE INTERACTIVA -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="glass-panel chart-card">
                        <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 gap-3">
                            <h5 class="m-0 section-title"><i class="fa-solid fa-list-check me-2" style="color: var(--blue);"></i> Estado de Confiabilidad por Unidad</h5>

                            <div class="d-flex align-items-center flex-wrap gap-2">
                                <label class="text-secondary small fw-bold"><i class="fa-solid fa-layer-group me-1" style="color: var(--blue);"></i>TIPO DE FLOTA:</label>
                                <select id="selectFiltroGrupo" class="select-kpi me-2" onchange="aplicarFiltrosTabla('grupo')">
                                    <option value="ALL">Todos</option>
                                    <option value="CONTRATO">Contrato / Propio</option>
                                    <option value="CLIENTE">Cliente</option>
                                    <option value="ALQUILADOS">Alquilado</option>
                                </select>

                                <label class="text-secondary small fw-bold"><i class="fa-solid fa-truck me-1" style="color: var(--orange);"></i>EQUIPO:</label>
                                <select id="selectFiltroEquipo" class="select-kpi me-2" onchange="aplicarFiltrosTabla('equipo')">
                                    {opciones_equipos_html}
                                </select>

                                <label class="text-secondary small fw-bold"><i class="fa-regular fa-calendar me-1"></i>DESDE:</label>
                                <input type="date" id="fechaInicio" class="input-kpi" value="{str_fmin}" onchange="aplicarFiltrosTabla('fecha')">

                                <label class="text-secondary small fw-bold ms-1"><i class="fa-regular fa-calendar me-1"></i>HASTA:</label>
                                <input type="date" id="fechaFin" class="input-kpi" value="{str_fmax}" onchange="aplicarFiltrosTabla('fecha')">

                                <label class="text-secondary small fw-bold ms-1"><i class="fa-solid fa-magnifying-glass me-1"></i></label>
                                <input type="text" id="buscadorEquipo" class="input-kpi" placeholder="Buscar equipo..." oninput="filtrarBusqueda(this.value)">

                                <button class="btn btn-sm btn-outline-secondary btn-reset" onclick="limpiarFiltros()"><i class="fa-solid fa-rotate-left me-1"></i>Reset</button>
                                <button class="btn btn-sm btn-export" onclick="exportarCSV()"><i class="fa-solid fa-file-csv me-1"></i>Exportar CSV</button>
                            </div>
                        </div>

                        <div class="table-wrapper">
                            <table class="table table-custom table-hover mb-0" id="tablaKPIs">
                                <thead>
                                    <tr>
                                        <th onclick="ordenarTabla(0,'text')">GRUPO <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(1,'text')">EQUIPO <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(2,'num')">% DM <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(3,'num')">DM META <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(4,'num')">BRECHA <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(5,'num')">MTBF <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(6,'num')">MTTR <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(7,'num')">FALLAS <i class="fa-solid fa-sort sort-icon"></i></th>
                                        <th onclick="ordenarTabla(8,'text')">ESTADO <i class="fa-solid fa-sort sort-icon"></i></th>
                                    </tr>
                                </thead>
                                <tbody id="tbodyKPIs">
                                </tbody>
                            </table>
                        </div>
                        <small class="text-secondary"><i class="fa-solid fa-circle-info me-1"></i>Las filas resaltadas en rojo indican equipos "Top Offender" — mayor consumo de disponibilidad de la flota en el periodo filtrado. Haz clic en un encabezado para ordenar.</small>
                    </div>
                </div>
            </div>

            <!-- KPIs POR EQUIPO (sincronizado con los filtros de Grupo/Equipo/Semana/Fecha de arriba) -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="glass-panel chart-card chart-container" id="panel_kpis_equipo">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-chart-column me-1"></i>KPIs por Equipo — Disponibilidad, Meta, MTTR y MTBF</span>
                            <div class="d-flex align-items-center gap-2">
                                <span class="text-secondary small">Sincronizado con los filtros de la tabla</span>
                                <button class="btn-fullscreen" onclick="toggleFullscreen('panel_kpis_equipo')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                            </div>
                        </div>
                        <div class="chart-scroll-x">
                            <div id="chartKpisEquipoWrap" style="min-width:900px;">
                                <div id="chartKpisEquipo" style="width:100%; height:460px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TOP OFENSORES -->
            <div class="row mt-2">
                <div class="col-12">
                    <div class="glass-panel chart-card chart-container" id="panel_top_ofensores">
                        <div class="chart-toolbar">
                            <span class="chart-toolbar-title"><i class="fa-solid fa-fire me-1" style="color: var(--critical);"></i>Top Ofensores — Mayor Pérdida de Disponibilidad</span>
                            <span class="text-secondary small">Sincronizado con los filtros de la tabla</span>
                        </div>
                        <div class="table-wrapper" style="max-height:420px;">
                            <table class="table table-custom table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th>EQUIPO</th>
                                        <th>HORAS DE PARADA</th>
                                        <th>TIPO DE FALLA</th>
                                        <th>ESTATUS</th>
                                        <th>TENDENCIA</th>
                                    </tr>
                                </thead>
                                <tbody id="tbodyTopOfensores"></tbody>
                            </table>
                        </div>
                        <small class="text-secondary"><i class="fa-solid fa-circle-info me-1"></i>Tendencia compara el %DM del equipo contra un periodo inmediatamente anterior de igual duración.</small>
                    </div>
                </div>
            </div>

            {mtbs_panel_html}

            {bkl_cards_panel_html}
        </div>

        <script>
            const datosSemanasPM = {json_pm_semanas};
            const catalogoEquipos = {json_catalogo};
            const rawIntervenciones = {json_raw_intervenciones};
            const TENDENCIAS_POR_CATEGORIA = {json_tendencias_categoria};
            const SEMANAS_PM_CHART = {json_semanas_pm_chart};
            const OTROS_DATA = {json_otros_data};
            const PARES_COLOR_ACTIVIDAD = {json_pares_color_actividad};
            const TIPOS_ACTIVIDAD_ORDEN = {json_tipos_actividad_orden};
            const MATRIZ_SEMANA_SISTEMA = {json_matriz_semana_sistema};
            const DONUT_COLOR_MAP = {json_donut_color_map};
            const DONUT_TOP6 = {json_donut_top6};
            const MATRIZ_MEDIANAS = {json_matrix_medianas};
            const MATRIX_LAYOUT_BASE = {json_matrix_layout_base};
            const GAUGE_LAYOUT_BASE = {json_gauge_layout_base};

            // --- Estado global de cross-filtering (Requerimiento 2) ---
            let filtroSistemaActivo = null;
            let filtroEquipoActivo = null;

            function actualizarKpiPM(semana) {{
                const data = datosSemanasPM[semana];
                if (data) {{
                    const valorEl = document.getElementById('kpiValuePM');
                    valorEl.innerText = data.pct + '%';
                    document.getElementById('kpiDetailPM').innerText = data.ejecutados + ' de ' + data.programados + ' ejecutados';

                    // Estado visual reactivo: color del valor + badge según el % de
                    // cumplimiento (>=90 en meta, 70-89 en curso, <70 crítico).
                    let color, claseBadge, icono, texto;
                    if (data.pct >= 90) {{
                        color = 'var(--ok)'; claseBadge = 'kpi-trend-up'; icono = 'fa-circle-check'; texto = 'En meta';
                    }} else if (data.pct >= 70) {{
                        color = 'var(--warning)'; claseBadge = 'kpi-trend-warn'; icono = 'fa-triangle-exclamation'; texto = 'En curso';
                    }} else {{
                        color = 'var(--critical)'; claseBadge = 'kpi-trend-down'; icono = 'fa-circle-exclamation'; texto = 'Crítico';
                    }}
                    valorEl.style.color = color;
                    document.getElementById('kpiEstadoPM').innerHTML =
                        `<span class="kpi-trend ${{claseBadge}}"><i class="fa-solid ${{icono}}"></i> ${{texto}}</span>`;
                }}
                sincronizarGraficoPM(semana);
                resaltarSemanaTrendPM(semana);
            }}

            // ============================================================
            // Selector de Semana (tarjeta KPI "Cumplimiento PM"): sincroniza el
            // gráfico "Desviación Mantenimiento Preventivo" (mismas trazas que
            // construye Python en fig_pm, solo se conmuta su visibilidad — la
            // matemática de %DM/consolidado global NO se toca aquí).
            // ============================================================
            function sincronizarGraficoPM(semana) {{
                const gd = document.getElementById('chartPMDesviacion');
                if (!gd || !window.Plotly || !gd.data) return;

                const idx = SEMANAS_PM_CHART.findIndex(s => String(s) === String(semana));
                if (idx === -1) return;

                const visibleMask = new Array(SEMANAS_PM_CHART.length * 2).fill(false);
                visibleMask[idx * 2] = true;
                visibleMask[idx * 2 + 1] = true;

                Plotly.restyle(gd, {{ visible: visibleMask }});
                Plotly.relayout(gd, {{
                    'title.text': '<b>Desviación Mantenimiento Preventivo — Semana ' + semana + '</b>',
                    'updatemenus[0].active': idx
                }});
            }}

            // Resalta en la tendencia semanal de PM la semana elegida en la tarjeta KPI.
            function resaltarSemanaTrendPM(semana) {{
                const gd = document.getElementById('chartTrendPM');
                if (!gd || !window.Plotly || !gd.data) return;

                Plotly.relayout(gd, {{
                    shapes: [{{
                        type: 'line', x0: semana, x1: semana, xref: 'x',
                        y0: 0, y1: 1, yref: 'paper',
                        line: {{ color: '#f7931e', width: 2, dash: 'dot' }}
                    }}]
                }});
            }}

            // ============================================================
            // "Dashboard Executive Premium" — Programado vs. Ejecutado por Tipo de
            // Actividad (Obras/Otras). Pares de color dedicados por tipo (Prog oscuro/
            // translúcido vs. Ejec vibrante/neón), esquinas superiores redondeadas
            // (marker.cornerradius), etiquetas SIEMPRE fuera de la barra en negrita
            // blanca, eje X anguiado y separación de grupos vía bargap/bargroupgap. El
            // efecto de profundidad/glow ("flotando") se aplica con CSS
            // `filter: drop-shadow(...)` sobre el contenedor (`.chart-otros-premium`) —
            // Plotly no soporta gradientes lineales dentro de una sola barra, así que
            // el "3D" se logra con color vibrante sólido + brillo de borde + sombra.
            // ============================================================
            function renderOtrosChart(semana) {{
                const datosSemana = OTROS_DATA.filter(d => String(d.semana) === String(semana));
                const wrap = document.getElementById('chartOtrosWrap');

                if (!datosSemana.length) {{
                    Plotly.react('chartOtrosActividades', [], {{
                        template: 'plotly_dark', paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                        annotations: [{{ text: 'Sin datos de Obras/Otras Actividades para esta semana', showarrow: false, font: {{ color: '#64748b' }} }}],
                        height: 300
                    }}, {{ displaylogo: false, responsive: true }});
                    return;
                }}

                const tiposPresentes = TIPOS_ACTIVIDAD_ORDEN.filter(t => datosSemana.some(d => d.tipo === t));
                const equiposUnicos = new Set(datosSemana.map(d => d.equipo));

                const traces = [];
                tiposPresentes.forEach(tipo => {{
                    const filas = datosSemana.filter(d => d.tipo === tipo).sort((a, b) => a.equipo.localeCompare(b.equipo));
                    const colores = PARES_COLOR_ACTIVIDAD[tipo] || PARES_COLOR_ACTIVIDAD['_DEFAULT'];

                    traces.push({{
                        type: 'bar',
                        name: tipo + ' (Prog)',
                        legendgroup: tipo,
                        x: filas.map(f => f.equipo),
                        y: filas.map(f => f.prog),
                        marker: {{
                            color: colores.prog,
                            opacity: 0.82,
                            cornerradius: 6,
                            line: {{ color: 'rgba(255,255,255,0.12)', width: 1 }}
                        }},
                        text: filas.map(f => '<b>' + f.prog.toFixed(1) + '</b>'),
                        textposition: 'outside',
                        textfont: {{ size: 11, color: '#ffffff', family: 'Inter, Segoe UI, sans-serif' }},
                        cliponaxis: false,
                        hovertemplate: '<b>%{{x}}</b><br>' + tipo + ' — Programadas: %{{y:.1f}} h<extra></extra>'
                    }});
                    traces.push({{
                        type: 'bar',
                        name: tipo + ' (Ejec)',
                        legendgroup: tipo,
                        x: filas.map(f => f.equipo),
                        y: filas.map(f => f.ejec),
                        marker: {{
                            color: colores.ejec,
                            cornerradius: 6,
                            line: {{ color: 'rgba(255,255,255,0.55)', width: 1.2 }}
                        }},
                        text: filas.map(f => '<b>' + f.ejec.toFixed(1) + '</b>'),
                        textposition: 'outside',
                        textfont: {{ size: 12, color: '#ffffff', family: 'Inter, Segoe UI, sans-serif' }},
                        cliponaxis: false,
                        hovertemplate: '<b>%{{x}}</b><br>' + tipo + ' — Ejecutadas: %{{y:.1f}} h<extra></extra>'
                    }});
                }});

                const layout = {{
                    template: 'plotly_dark',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ family: 'Inter, Segoe UI, sans-serif', color: '#e2e8f0' }},
                    hoverlabel: {{ bgcolor: 'rgba(21,28,44,0.95)', bordercolor: '#a78bfa', font: {{ family: 'JetBrains Mono, monospace', size: 12, color: '#f8fafc' }} }},
                    barmode: 'group',
                    bargap: 0.3,
                    bargroupgap: 0.12,
                    xaxis: {{ tickangle: -45, gridcolor: 'rgba(148,163,184,0.08)', tickfont: {{ size: 10.5 }} }},
                    yaxis: {{ title: 'Horas', gridcolor: 'rgba(148,163,184,0.12)' }},
                    legend: {{ orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'center', x: 0.5, font: {{ size: 10.5 }} }},
                    margin: {{ l: 55, r: 20, t: 40, b: 100 }},
                    height: 520
                }};

                if (wrap) {{ wrap.style.minWidth = Math.max(900, equiposUnicos.size * 60) + 'px'; }}
                Plotly.react('chartOtrosActividades', traces, layout, {{ displaylogo: false, responsive: true }});

                const gdOtros = document.getElementById('chartOtrosActividades');
                gdOtros.removeAllListeners && gdOtros.removeAllListeners('plotly_click');
                gdOtros.on('plotly_click', function(evt) {{
                    if (!evt || !evt.points || !evt.points.length) return;
                    activarFiltroEquipo(evt.points[0].x);
                }});
            }}

            // ============================================================
            // Velocímetro DM Global — SIN filtro propio. Se llama exclusivamente desde
            // `recalcularKPIsGlobales`, con los MISMOS dmProm/metaProm/n que ya muestra
            // la tarjeta KPI superior "DM GLOBAL" — un solo cálculo (universo filtrado
            // por KPIS SUPERIORES: Periodo/Rango de fechas/Flota), dos visualizaciones.
            // El layout base (fondo, título, márgenes) vive en GAUGE_LAYOUT_BASE y se
            // reutiliza sin cambios; solo se reconstruye la traza 'indicator'.
            // ============================================================
            function renderGauge(dmProm, metaProm, n) {{
                const brecha = dmProm - metaProm;

                let colorAnillo;
                if (dmProm >= metaProm) {{ colorAnillo = '#10b981'; }}
                else if (dmProm >= 85) {{ colorAnillo = '#38bdf8'; }}
                else {{ colorAnillo = '#dc2626'; }}

                const trace = {{
                    type: 'indicator',
                    mode: 'gauge+number+delta',
                    value: dmProm,
                    number: {{ suffix: '%', font: {{ size: 46, color: '#f8fafc', family: 'Plus Jakarta Sans' }} }},
                    delta: {{ reference: metaProm, increasing: {{ color: '#10b981' }}, decreasing: {{ color: '#dc2626' }}, font: {{ size: 14 }} }},
                    title: {{
                        text: '<b>DM GLOBAL DE FLOTA</b><br><span style="font-size:11px;color:#94a3b8">vs. Meta Contractual</span>',
                        font: {{ size: 15, color: '#e2e8f0' }}
                    }},
                    gauge: {{
                        axis: {{ range: [0, 100], tickcolor: 'rgba(148,163,184,0.4)', tickwidth: 1, tickfont: {{ size: 10, color: '#64748b' }} }},
                        bar: {{ color: colorAnillo, thickness: 0.16 }},
                        bgcolor: 'rgba(255,255,255,0.03)',
                        borderwidth: 0,
                        steps: [{{ range: [0, 100], color: 'rgba(148,163,184,0.06)' }}],
                        threshold: {{ line: {{ color: '#f7931e', width: 3 }}, thickness: 0.9, value: metaProm }}
                    }}
                }};

                Plotly.react('chartGaugeDM', [trace], GAUGE_LAYOUT_BASE, {{ displaylogo: false, responsive: true }});

                if (n === 0) {{
                    document.getElementById('gaugeMetaBadge').innerText = 'Meta Contractual: —';
                    const brechaVacia = document.getElementById('gaugeBrechaBadge');
                    brechaVacia.innerText = 'Sin datos para este filtro';
                    brechaVacia.classList.remove('kpi-trend-up', 'kpi-trend-down');
                    brechaVacia.classList.add('gauge-badge-neutral');
                    document.getElementById('gaugeUnidadesBadge').innerText = 'Unidades Evaluadas: 0 equipo(s)';
                    return;
                }}

                document.getElementById('gaugeMetaBadge').innerText = 'Meta Contractual: ' + metaProm.toFixed(1) + '%';
                const brechaEl = document.getElementById('gaugeBrechaBadge');
                brechaEl.classList.remove('gauge-badge-neutral');
                brechaEl.innerText = 'Brecha / Desviación: ' + (brecha >= 0 ? '+' : '') + brecha.toFixed(1) + ' pp';
                brechaEl.classList.remove('kpi-trend-up', 'kpi-trend-down');
                brechaEl.classList.add(brecha >= 0 ? 'kpi-trend-up' : 'kpi-trend-down');
                document.getElementById('gaugeUnidadesBadge').innerText = 'Unidades Evaluadas: ' + n + ' equipo(s)';
            }}

            // ============================================================
            // REQUERIMIENTO 1: Botón de Enfoque / Fullscreen (Modo Cine)
            // ============================================================
            function toggleFullscreen(panelId) {{
                const panel = document.getElementById(panelId);
                if (!panel) return;
                panel.classList.toggle('chart-fullscreen');

                const btn = panel.querySelector('.btn-fullscreen i');
                if (panel.classList.contains('chart-fullscreen')) {{
                    if (btn) {{ btn.classList.remove('fa-expand'); btn.classList.add('fa-compress'); }}
                }} else {{
                    if (btn) {{ btn.classList.remove('fa-compress'); btn.classList.add('fa-expand'); }}
                }}

                // Redimensionar el gráfico Plotly contenido, si existe
                const plotDiv = panel.querySelector('.js-plotly-plot') || panel.querySelector('div[id^="chart"]');
                if (plotDiv && window.Plotly) {{
                    setTimeout(() => Plotly.Plots.resize(plotDiv), 260);
                }}
            }}

            // ============================================================
            // REQUERIMIENTO 1 + 2: Gráfico DM (JS-driven) — Top N + cross-filter por clic
            // ============================================================
            // DM vs. Meta — 100% reactivo a los filtros globales (Rango de Fechas + Tipo de
            // Flota): recibe las MISMAS `filas` ya filtradas que arma `renderizarTabla`
            // (única fuente de verdad, ídem tarjetas KPI y Velocímetro). El selector local
            // "Top N" solo decide cuántas se muestran, no re-filtra ni recalcula nada.
            function renderDMChart(filas) {{
                const topN = document.getElementById('selectTopNDM').value;

                // Sin dato oficial ni fallback (dmPct === null): no se puede graficar, se excluye.
                let datos = (filas || [])
                    .filter(f => f.dmPct != null)
                    .map(f => ({{
                        equipo: f.eq.equipo,
                        dm: f.dmPct,
                        meta: f.eq.dm_meta,
                        brecha: f.dmPct - f.eq.dm_meta,
                        cumple: f.dmPct >= f.eq.dm_meta,
                        estado: f.dmPct >= f.eq.dm_meta ? 'CUMPLE META' : 'CRÍTICO',
                        dias_sin_falla: f.eq.dias_sin_falla,
                    }}))
                    .sort((a, b) => a.dm - b.dm); // peor primero

                if (topN !== 'ALL') {{
                    datos = datos.slice(0, parseInt(topN, 10));
                }}
                // Para lectura natural en barras horizontales (peor arriba), invertimos el orden de trazado
                datos = datos.slice().reverse();

                if (!datos.length) {{
                    Plotly.react('chartDM', [], {{
                        template: 'plotly_dark', paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                        annotations: [{{ text: 'Sin datos para el filtro actual', showarrow: false, font: {{ color: '#64748b' }} }}],
                        height: 320
                    }}, {{ displaylogo: false, responsive: true }});
                    return;
                }}

                const colores = datos.map(d => d.cumple ? '#10b981' : '#dc2626');
                const textos = datos.map(d => d.dm.toFixed(1) + '%');
                const diasTxt = datos.map(d => d.dias_sin_falla != null ? (d.dias_sin_falla + ' días') : 'Sin registro');

                const traceBarras = {{
                    type: 'bar',
                    orientation: 'h',
                    x: datos.map(d => d.dm),
                    y: datos.map(d => d.equipo),
                    marker: {{ color: colores, line: {{ width: 0 }} }},
                    text: textos,
                    textposition: 'outside',
                    textfont: {{ family: 'Plus Jakarta Sans', size: 11, color: '#e5e7eb' }},
                    customdata: datos.map((d, idx) => [d.meta, d.brecha, d.estado, diasTxt[idx]]),
                    hovertemplate:
                        '<b>%{{y}}</b><br>' +
                        'Disponibilidad: <b>%{{x:.1f}}%</b><br>' +
                        'Meta: %{{customdata[0]:.1f}}%<br>' +
                        'Brecha: %{{customdata[1]:+.1f}} pp<br>' +
                        'Días sin fallas: %{{customdata[3]}}<br>' +
                        'Estado: %{{customdata[2]}}<extra></extra>',
                    name: '% DM'
                }};

                const traceMeta = {{
                    type: 'scatter',
                    mode: 'markers',
                    x: datos.map(d => d.meta),
                    y: datos.map(d => d.equipo),
                    marker: {{ color: '#f7931e', size: 12, symbol: 'diamond', line: {{ width: 1, color: '#0b0f19' }} }},
                    name: 'Meta Contractual',
                    hovertemplate: '<b>%{{y}}</b><br>Meta: %{{x:.1f}}%<extra></extra>'
                }};

                const layout = {{
                    template: 'plotly_dark',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ family: 'Inter, Segoe UI, sans-serif', color: '#e2e8f0' }},
                    // automargin evita que las etiquetas de equipo (eje Y) o el texto de las
                    // barras (eje X, textposition 'outside') se corten o se monten sobre el
                    // área de trazado — Plotly expande el margen lo necesario en cada render.
                    xaxis: {{ ticksuffix: '%', gridcolor: 'rgba(148,163,184,0.12)', automargin: true }},
                    yaxis: {{ gridcolor: 'rgba(148,163,184,0.06)', automargin: true }},
                    hovermode: 'closest',
                    hoverlabel: {{ bgcolor: 'rgba(21,28,44,0.95)', bordercolor: '#38bdf8', font: {{ family: 'JetBrains Mono, monospace', size: 12, color: '#f8fafc' }} }},
                    legend: {{ orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'right', x: 1 }},
                    margin: {{ l: 60, r: 30, t: 30, b: 10 }},
                    height: Math.max(320, datos.length * 34)
                }};

                Plotly.react('chartDM', [traceBarras, traceMeta], layout, {{ displaylogo: false, responsive: true }});

                const gd = document.getElementById('chartDM');
                gd.removeAllListeners && gd.removeAllListeners('plotly_click');
                gd.on('plotly_click', function(evt) {{
                    if (!evt || !evt.points || !evt.points.length) return;
                    const equipoClic = evt.points[0].y;
                    activarFiltroEquipo(equipoClic);
                }});
            }}

            // ============================================================
            // Pareto de Sistemas Críticos — 100% reactivo a los filtros globales (Rango de
            // Fechas + Tipo de Flota): recalcula Horas de Parada/N° Eventos por sistema
            // considerando ÚNICAMENTE intervenciones CORRECTIVAS que (a) ocurren dentro del
            // rango de fechas y (b) pertenecen a un equipo de la flota/selección actual.
            // Usa `rawIntervenciones` directo (no `intervencionesFiltradas`): el cross-filter
            // de sistema (clic en una barra) no debe autoocultar las demás barras del propio
            // Pareto — solo acota el numerador de %DM en la tabla (comportamiento ya existente).
            // Top N / Top Criticidad / métrica siguen siendo un control LOCAL de cuántas
            // barras mostrar, no un filtro de datos.
            // ============================================================
            function renderParetoChart(equiposFiltrados, dInicioFiltro, dFinFiltro) {{
                const metrica = document.getElementById('selectMetricaPareto').value;
                const topN = document.getElementById('selectTopNPareto').value;

                const campoMetrica = metrica === 'horas' ? 'horas' : (metrica === 'eventos' ? 'eventos' : 'mttr');
                const etiquetaMetrica = metrica === 'horas' ? 'Horas de Parada' : (metrica === 'eventos' ? 'N° de Eventos' : 'MTTR (h/evento)');

                const equiposSet = new Set((equiposFiltrados || []).map(e => e.equipo));
                const correctivos = rawIntervenciones.filter(i => {{
                    if (!equiposSet.has(i.equipo)) return false;
                    if (!i.sistema) return false;
                    if (!(i.tipo || '').toUpperCase().includes('CORRECTIV')) return false;
                    if (!i.inicio) return false;
                    const fIni = new Date(i.inicio);
                    const fFin = i.fin ? new Date(i.fin) : new Date();
                    return fIni < dFinFiltro && fFin > dInicioFiltro;
                }});

                const porSistema = {{}};
                correctivos.forEach(i => {{
                    if (!porSistema[i.sistema]) porSistema[i.sistema] = {{ horas: 0, eventos: 0 }};
                    porSistema[i.sistema].horas += (i.horas_netas || 0);
                    porSistema[i.sistema].eventos += 1;
                }});

                let datos = Object.keys(porSistema).map(sistema => {{
                    const d = porSistema[sistema];
                    return {{
                        sistema: sistema,
                        horas: d.horas,
                        eventos: d.eventos,
                        mttr: d.eventos > 0 ? d.horas / d.eventos : 0,
                    }};
                }});

                const maxHoras = Math.max(1, ...datos.map(d => d.horas));
                const maxEventos = Math.max(1, ...datos.map(d => d.eventos));
                datos.forEach(d => {{ d.criticidad = 0.5 * (d.horas / maxHoras) + 0.5 * (d.eventos / maxEventos); }});

                if (!datos.length) {{
                    Plotly.react('chartPareto', [], {{
                        template: 'plotly_dark', paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                        annotations: [{{ text: 'Sin intervenciones correctivas para el filtro actual', showarrow: false, font: {{ color: '#64748b' }} }}],
                        height: 460
                    }}, {{ displaylogo: false, responsive: true }});
                    return;
                }}

                if (topN === 'crit10') {{
                    datos.sort((a, b) => b.criticidad - a.criticidad);
                    datos = datos.slice(0, 10);
                }} else {{
                    datos.sort((a, b) => b[campoMetrica] - a[campoMetrica]);
                    if (topN !== 'ALL') {{ datos = datos.slice(0, parseInt(topN, 10)); }}
                }}

                // % acumulado calculado sobre el subconjunto visible y la métrica seleccionada
                const totalMetrica = datos.reduce((acc, d) => acc + d[campoMetrica], 0) || 1;
                let acumulado = 0;
                const pctAcumulado = datos.map(d => {{
                    acumulado += d[campoMetrica];
                    return (acumulado / totalMetrica * 100);
                }});

                const traceBarras = {{
                    type: 'bar',
                    x: datos.map(d => d.sistema),
                    y: datos.map(d => d[campoMetrica]),
                    marker: {{ color: '#f7931e' }},
                    text: datos.map(d => d[campoMetrica].toFixed(1)),
                    textposition: 'outside',
                    name: etiquetaMetrica,
                    customdata: datos.map(d => [d.horas, d.eventos, d.mttr]),
                    hovertemplate:
                        '<b>%{{x}}</b><br>' +
                        etiquetaMetrica + ': <b>%{{y:.1f}}</b><br>' +
                        'Horas parada: %{{customdata[0]:.1f}} h<br>' +
                        'N° eventos: %{{customdata[1]}}<br>' +
                        'MTTR sistema: %{{customdata[2]:.1f}} h<extra></extra>'
                }};

                const traceAcumulado = {{
                    type: 'scatter',
                    mode: 'lines+markers',
                    x: datos.map(d => d.sistema),
                    yaxis: 'y2',
                    y: pctAcumulado,
                    line: {{ color: '#38bdf8', width: 2, dash: 'dot' }},
                    marker: {{ size: 7, color: '#38bdf8', line: {{ width: 1, color: '#fff' }} }},
                    name: '% Acumulado',
                    hovertemplate: '<b>%{{x}}</b><br>Acumulado: <b>%{{y:.1f}}%</b><extra></extra>'
                }};

                const layout = {{
                    template: 'plotly_dark',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ family: 'Inter, Segoe UI, sans-serif', color: '#e2e8f0' }},
                    // automargin en ambos ejes Y (izq/der) evita que los títulos "Horas de
                    // Parada"/"% Acumulado" queden montados sobre los números de los ticks;
                    // xaxis con automargin evita que los nombres de sistema se corten.
                    xaxis: {{ automargin: true, tickangle: -20 }},
                    yaxis: {{ title: etiquetaMetrica, gridcolor: 'rgba(148,163,184,0.12)', automargin: true }},
                    yaxis2: {{ title: '% Acumulado', overlaying: 'y', side: 'right', range: [0, 105], showgrid: false, automargin: true }},
                    hovermode: 'x unified',
                    hoverlabel: {{ bgcolor: 'rgba(21,28,44,0.95)', bordercolor: '#38bdf8', font: {{ family: 'JetBrains Mono, monospace', size: 12, color: '#f8fafc' }} }},
                    legend: {{ orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'right', x: 1 }},
                    margin: {{ l: 60, r: 50, t: 30, b: 60 }},
                    height: 460,
                    shapes: [{{
                        type: 'line', x0: 0, x1: 1, xref: 'paper', y0: 80, y1: 80, yref: 'y2',
                        line: {{ color: '#f59e0b', width: 1, dash: 'dash' }}
                    }}]
                }};

                Plotly.react('chartPareto', [traceBarras, traceAcumulado], layout, {{ displaylogo: false, responsive: true }});

                const gd = document.getElementById('chartPareto');
                gd.removeAllListeners && gd.removeAllListeners('plotly_click');
                gd.on('plotly_click', function(evt) {{
                    if (!evt || !evt.points || !evt.points.length) return;
                    const sistemaClic = evt.points[0].x;
                    activarFiltroSistema(sistemaClic);
                }});
            }}

            // ============================================================
            // Donut de Inoperatividad por Sistema — filtro local de Semana
            // (paleta fija por sistema: Top 6 global + "OTROS", igual que antes)
            // ============================================================
            function renderDonutChart(semana) {{
                const datosSemana = MATRIZ_SEMANA_SISTEMA[semana] || {{}};

                let labels = [];
                let values = [];
                let otrosHoras = 0;

                DONUT_TOP6.forEach(sist => {{
                    const h = datosSemana[sist] || 0;
                    if (h > 0) {{ labels.push(sist); values.push(h); }}
                }});

                Object.keys(datosSemana).forEach(sist => {{
                    if (!DONUT_TOP6.includes(sist)) {{ otrosHoras += datosSemana[sist]; }}
                }});
                if (otrosHoras > 0) {{ labels.push('OTROS'); values.push(otrosHoras); }}

                const colores = labels.map(l => DONUT_COLOR_MAP[l] || '#64748b');
                const total = values.reduce((acc, v) => acc + v, 0);

                const trace = {{
                    type: 'pie',
                    labels: labels,
                    values: values,
                    hole: 0.58,
                    marker: {{ colors: colores, line: {{ color: '#0b0f19', width: 2 }} }},
                    textinfo: 'label+percent',
                    textfont: {{ size: 12, color: '#e2e8f0' }},
                    hovertemplate: '<b>%{{label}}</b><br>Horas inoperativas: %{{value:.1f}} h<br>Participación: %{{percent}}<extra></extra>'
                }};

                const layout = {{
                    template: 'plotly_dark',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ family: 'Inter, Segoe UI, sans-serif', color: '#e2e8f0' }},
                    hoverlabel: {{ bgcolor: 'rgba(21,28,44,0.95)', bordercolor: '#38bdf8', font: {{ family: 'JetBrains Mono, monospace', size: 12, color: '#f8fafc' }} }},
                    showlegend: true,
                    legend: {{ orientation: 'v', yanchor: 'middle', y: 0.5, xanchor: 'left', x: 1.02 }},
                    height: 420,
                    margin: {{ l: 10, r: 120, t: 20, b: 10 }},
                    annotations: [{{ text: total.toFixed(0) + 'h<br>Total', x: 0.5, y: 0.5, font: {{ size: 16, color: '#e2e8f0' }}, showarrow: false }}]
                }};

                Plotly.react('chartDonut', [trace], layout, {{ displaylogo: false, responsive: true }});
            }}

            // ============================================================
            // Matriz de Criticidad MTBF vs. MTTR — filtros PROPIOS (Flota + Rango de
            // Fechas), independientes de la barra "KPIS SUPERIORES". Los valores
            // graficados (MTBF/MTTR/Fallas) se recalculan 100% en vivo con
            // `calcularKpisDinamico` para el rango elegido en ESTA matriz — misma
            // función/fuente única de verdad que usan la tabla principal, el
            // Velocímetro y las tarjetas KPI. Los filtros de esta matriz deciden el
            // rango de cálculo Y qué equipos se muestran (por categoría y por
            // actividad dentro del rango, usando `rawIntervenciones`). Sin selector de
            // semana. Los ejes/medianas/líneas punteadas/anotaciones de cuadrante viven
            // en MATRIX_LAYOUT_BASE/MATRIZ_MEDIANAS (capturados tal cual desde el
            // layout que calculó Python) y no cambian con estos filtros — son
            // benchmarks de referencia, no un KPI por equipo.
            // ============================================================
            function obtenerCuadranteCriticidad(mtbf, mttr) {{
                const medMTBF = MATRIZ_MEDIANAS.mtbf;
                const medMTTR = MATRIZ_MEDIANAS.mttr;
                if (mtbf < medMTBF && mttr >= medMTTR) return 'Altamente Crítico (Bajo MTBF / Alto MTTR)';
                if (mtbf >= medMTBF && mttr >= medMTTR) return 'Vigilar (Alto MTBF / Alto MTTR)';
                if (mtbf < medMTBF && mttr < medMTTR) return 'Revisar Frecuencia (Bajo MTBF / Bajo MTTR)';
                return 'Clase Mundial (Alto MTBF / Bajo MTTR)';
            }}

            function renderMatrixChart() {{
                const flotaSel = document.getElementById('matrixSelectFlota').value;
                const fIniVal = document.getElementById('matrixFechaInicio').value;
                const fFinVal = document.getElementById('matrixFechaFin').value;
                const dInicio = new Date(fIniVal + "T00:00:00");
                const dFin = new Date(fFinVal + "T23:59:59");

                // "Unidades activas en el periodo": equipo con al menos una intervención
                // (de cualquier tipo) que se traslape con el rango de fechas seleccionado.
                // Determina SOLO qué equipos entran a la matriz.
                const equiposActivos = new Set();
                rawIntervenciones.forEach(i => {{
                    if (!i.inicio || equiposActivos.has(i.equipo)) return;
                    const fIni = new Date(i.inicio);
                    const fFin = i.fin ? new Date(i.fin) : new Date();
                    if (fIni < dFin && fFin > dInicio) equiposActivos.add(i.equipo);
                }});

                // MTBF/MTTR/Fallas 100% dinámicos para el rango DESDE/HASTA propio de esta
                // matriz — MISMA función `calcularKpisDinamico` que usa la tabla principal,
                // el Velocímetro y las tarjetas KPI (fuente única de verdad). MATRIZ_GLOBAL
                // ya no se usa para los valores; solo `catalogoEquipos` aporta categoría/meta.
                const datos = catalogoEquipos
                    .filter(e => (flotaSel === 'ALL' || e.categoria === flotaSel) && equiposActivos.has(e.equipo))
                    .map(e => {{
                        const k = calcularKpisDinamico(e.equipo, fIniVal, fFinVal);
                        return {{
                            equipo: e.equipo, mtbf: k.mtbf, mttr: k.mttr, fallas: k.fallas,
                            estado: k.dm >= e.dm_meta ? 'Cumple Meta' : 'Crítico'
                        }};
                    }});

                if (!datos.length) {{
                    Plotly.react('chartMatrixCriticidad', [], MATRIX_LAYOUT_BASE, {{ displaylogo: false, responsive: true }});
                    return;
                }}

                // Solo se etiqueta con texto (código de equipo) a las unidades "fuera de la
                // zona deseada" (fuera de meta contractual / Crítico), para evitar el
                // solapamiento de etiquetas cuando hay muchas burbujas agrupadas; el resto
                // se identifica igual vía el tooltip enriquecido al pasar el cursor.
                const grupos = {{
                    'Cumple Meta': {{ color: '#10b981', datos: [] }},
                    'Crítico': {{ color: '#dc2626', datos: [] }}
                }};
                datos.forEach(d => {{ (grupos[d.estado] || grupos['Crítico']).datos.push(d); }});

                const maxFallas = Math.max(1, ...datos.map(d => d.fallas));
                const sizeref = 2 * maxFallas / (42 * 42);

                const traces = Object.keys(grupos)
                    .filter(k => grupos[k].datos.length > 0)
                    .map(k => {{
                        const grupo = grupos[k];
                        return {{
                            type: 'scatter',
                            mode: 'markers+text',
                            x: grupo.datos.map(d => d.mtbf),
                            y: grupo.datos.map(d => d.mttr),
                            text: grupo.datos.map(d => d.estado === 'Crítico' ? d.equipo : ''),
                            textposition: 'top center',
                            textfont: {{ size: 10, color: '#e2e8f0' }},
                            marker: {{
                                size: grupo.datos.map(d => d.fallas),
                                sizemode: 'area',
                                sizeref: sizeref,
                                color: grupo.color,
                                line: {{ width: 1, color: '#0d1b2e' }}
                            }},
                            name: k,
                            customdata: grupo.datos.map(d => [d.equipo, d.fallas, obtenerCuadranteCriticidad(d.mtbf, d.mttr)]),
                            hovertemplate:
                                '<b>%{{customdata[0]}}</b><br>' +
                                'MTBF: %{{x:.1f}} h<br>' +
                                'MTTR: %{{y:.1f}} h<br>' +
                                'N° Fallas: %{{customdata[1]}}<br>' +
                                'Cuadrante: %{{customdata[2]}}<extra></extra>'
                        }};
                    }});

                Plotly.react('chartMatrixCriticidad', traces, MATRIX_LAYOUT_BASE, {{ displaylogo: false, responsive: true }});

                const gdMatrix = document.getElementById('chartMatrixCriticidad');
                gdMatrix.removeAllListeners && gdMatrix.removeAllListeners('plotly_click');
                gdMatrix.on('plotly_click', function(evt) {{
                    if (!evt || !evt.points || !evt.points.length || !evt.points[0].customdata) return;
                    activarFiltroEquipo(evt.points[0].customdata[0]);
                }});
            }}

            // ============================================================
            // REQUERIMIENTO 2: Interactividad cruzada (cross-filtering bidireccional)
            // ============================================================
            function mostrarChipFiltro() {{
                const chip = document.getElementById('chipFiltroCross');
                const texto = document.getElementById('chipFiltroCrossTexto');
                const partes = [];
                if (filtroEquipoActivo) partes.push('EQUIPO: ' + filtroEquipoActivo);
                if (filtroSistemaActivo) partes.push('SISTEMA: ' + filtroSistemaActivo);

                if (partes.length === 0) {{
                    chip.style.display = 'none';
                    return;
                }}
                texto.innerText = 'Filtrando por: ' + partes.join(' + ') + ' (clic para limpiar)';
                chip.style.display = 'inline-flex';
            }}

            // El módulo MTBS es independiente en su CÁLCULO (no se toca su lógica ni sus
            // datos aquí), pero reacciona en su UI al filtro cruzado global — se resalta
            // (no se oculta) el equipo activo en sus gráficos, para no perder el contexto
            // comparativo. Chequeo defensivo `typeof === 'function'` porque estas
            // funciones viven en el <script> del módulo MTBS, cargado después.
            function refrescarModuloMtbsPorFiltroCruzado() {{
                if (typeof renderMtbsCorrelacionHabitos === 'function') {{ renderMtbsCorrelacionHabitos(); }}
            }}

            function activarFiltroEquipo(equipo) {{
                filtroEquipoActivo = equipo;
                const select = document.getElementById('selectFiltroEquipo');
                if (select) select.value = equipo;
                mostrarChipFiltro();
                aplicarFiltrosTabla('cross-equipo');
                refrescarModuloMtbsPorFiltroCruzado();
            }}

            function activarFiltroSistema(sistema) {{
                filtroSistemaActivo = sistema;
                mostrarChipFiltro();
                aplicarFiltrosTabla('cross-sistema');
            }}

            function limpiarFiltroCross() {{
                filtroEquipoActivo = null;
                filtroSistemaActivo = null;
                const select = document.getElementById('selectFiltroEquipo');
                if (select) select.value = 'ALL';
                mostrarChipFiltro();
                aplicarFiltrosTabla('cross-clear');
                refrescarModuloMtbsPorFiltroCruzado();
            }}

            function calcularHorasInopExactas(intervenciones, dInicioFiltro, dFinFiltro) {{
                if (intervenciones.length === 0) return 0;

                let intervalos = [];
                const now = new Date();

                intervenciones.forEach(r => {{
                    if (!r.inicio) return;

                    let fInicioInterv = new Date(r.inicio);
                    let fFinInterv;

                    if (!r.fin || r.fin.trim() === "") {{
                        fFinInterv = now;
                    }} else {{
                        fFinInterv = new Date(r.fin);
                    }}

                    if (fInicioInterv < dFinFiltro && fFinInterv > dInicioFiltro) {{
                        let iniAcotado = fInicioInterv > dInicioFiltro ? fInicioInterv : dInicioFiltro;
                        let finAcotado = fFinInterv < dFinFiltro ? fFinInterv : dFinFiltro;

                        if (finAcotado > iniAcotado) {{
                            intervalos.push([iniAcotado.getTime(), finAcotado.getTime()]);
                        }}
                    }}
                }});

                if (intervalos.length === 0) return 0;

                intervalos.sort((a, b) => a[0] - b[0]);
                let merged = [intervalos[0]];

                for (let i = 1; i < intervalos.length; i++) {{
                    let prev = merged[merged.length - 1];
                    let curr = intervalos[i];
                    if (curr[0] <= prev[1]) {{
                        prev[1] = Math.max(prev[1], curr[1]);
                    }} else {{
                        merged.push(curr);
                    }}
                }}

                let msTotal = 0;
                merged.forEach(inv => msTotal += (inv[1] - inv[0]));
                return msTotal / (1000 * 3600);
            }}

            // ============================================================
            // FUENTE ÚNICA DE VERDAD — réplica EXACTA (línea por línea) de la función
            // Python `calcular_kpis_dinamico_periodo`, que a su vez replica las macros
            // VBA 'CalcularKPIsCompletos'/'CalcularDisponibilidadDefinitiva'. Es la que
            // realmente corre cuando el usuario mueve DESDE/HASTA en el navegador (el
            // dashboard es HTML estático, no hay servidor Python escuchando esos
            // cambios). Si se modifica esta función, la versión Python debe
            // actualizarse igual — y viceversa.
            // ============================================================
            function calcularKpisDinamico(codigoEquipo, fechaDesdeStr, fechaHastaStr) {{
                const fechaInicioFiltro = new Date(fechaDesdeStr + "T00:00:00");
                const fechaFinFiltro = new Date(fechaHastaStr + "T00:00:00");
                fechaFinFiltro.setDate(fechaFinFiltro.getDate() + 1);
                const horasMes = (fechaFinFiltro - fechaInicioFiltro) / (1000 * 3600);

                const subs = rawIntervenciones.filter(i => i.equipo === codigoEquipo);
                const subsPrev = [];
                const subsCorr = [];
                let fallas = 0;
                let fallaEnCurso = false;

                subs.forEach(i => {{
                    if (!i.inicio) return;
                    const ini = new Date(i.inicio);
                    const abierta = !i.fin || i.fin.trim() === '';
                    const fin = abierta ? new Date() : new Date(i.fin);
                    if (fin <= ini) return;
                    if (!(ini < fechaFinFiltro && fin > fechaInicioFiltro)) return;

                    const tipo = (i.tipo || '').toUpperCase();
                    const esCorrectivo = tipo.includes('CORRECTIV') || tipo.includes('FALLA') || tipo.includes('EMERGENCIA');

                    if (esCorrectivo) {{
                        subsCorr.push(i);
                        fallas++;
                        if (abierta) fallaEnCurso = true;
                    }} else {{
                        subsPrev.push(i);
                    }}
                }});

                // Fusión de traslapes POR SEPARADO (Preventivo/Correctivo) — reutiliza
                // `calcularHorasInopExactas`, que ya filtra por solape + acota al rango +
                // fusiona; aquí solo se le pasa cada subconjunto ya clasificado por tipo.
                const hrsPrev = calcularHorasInopExactas(subsPrev, fechaInicioFiltro, fechaFinFiltro);
                const hrsCorr = calcularHorasInopExactas(subsCorr, fechaInicioFiltro, fechaFinFiltro);
                const hrsInopTotal = hrsPrev + hrsCorr;
                const hrsOperativas = Math.max(0, horasMes - hrsInopTotal);

                const mttr = fallas > 0 ? hrsCorr / fallas : 0;
                const mtbf = fallas > 0 ? hrsOperativas / fallas : hrsOperativas;
                const pctDm = horasMes > 0 ? Math.max(0, (horasMes - hrsInopTotal) / horasMes) * 100 : 0;

                return {{
                    dm: pctDm, mtbf: mtbf, mttr: mttr, fallas: fallas,
                    horasInoperativas: hrsInopTotal, fallaEnCurso: fallaEnCurso
                }};
            }}

            let filasCalculadasCache = [];

            function renderizarTabla(intervencionesFiltradas, dInicioFiltro, dFinFiltro, horasPeriodo, equipoSeleccionado, grupoSeleccionado) {{
                const tbody = document.getElementById('tbodyKPIs');
                let equiposAMostrar = catalogoEquipos;

                if (grupoSeleccionado && grupoSeleccionado !== 'ALL') {{
                    equiposAMostrar = equiposAMostrar.filter(e => e.categoria === grupoSeleccionado);
                }}
                if (equipoSeleccionado && equipoSeleccionado !== 'ALL') {{
                    equiposAMostrar = equiposAMostrar.filter(e => e.equipo === equipoSeleccionado);
                }}

                // FUENTE ÚNICA DE VERDAD: %DM/MTBF/MTTR/Fallas se recalculan 100% en vivo
                // para el rango DESDE/HASTA actual, para CUALQUIER equipo (Contrato o
                // Cliente) — ver `calcularKpisDinamico` (réplica exacta de las macros VBA).
                const fIniVal = document.getElementById('fechaInicio').value;
                const fFinVal = document.getElementById('fechaFin').value;

                let filas = [];

                equiposAMostrar.forEach(eq => {{
                    let subs = intervencionesFiltradas.filter(i => i.equipo === eq.equipo);
                    let inop = calcularHorasInopExactas(subs, dInicioFiltro, dFinFiltro);

                    let subsEnRango = subs.filter(r => {{
                        if (!r.inicio) return false;
                        let fIni = new Date(r.inicio);
                        let fFin = r.fin ? new Date(r.fin) : new Date();
                        return (fIni < dFinFiltro && fFin > dInicioFiltro);
                    }});

                    const kpisDinamicos = calcularKpisDinamico(eq.equipo, fIniVal, fFinVal);
                    let dmPct = kpisDinamicos.dm;
                    let mtbf = kpisDinamicos.mtbf;
                    let mttr = kpisDinamicos.mttr;
                    let fallas = kpisDinamicos.fallas;

                    // Sistema predominante (mayor horas acumuladas dentro del rango filtrado) —
                    // mismo criterio de agregación que ya usa el Pareto/Donut de Sistemas
                    // (suma de horas_netas por sistema, sin fusión de intervalos), para
                    // identificar el "Tipo de Falla" típico de cada equipo en Top Ofensores.
                    let horasPorSistema = {{}};
                    subsEnRango.forEach(r => {{
                        let sist = (r.sistema || '').trim();
                        if (!sist) return;
                        horasPorSistema[sist] = (horasPorSistema[sist] || 0) + (r.horas_netas || 0);
                    }});
                    let sistemaPredominante = null;
                    let maxHorasSistema = 0;
                    Object.keys(horasPorSistema).forEach(sist => {{
                        if (horasPorSistema[sist] > maxHorasSistema) {{
                            maxHorasSistema = horasPorSistema[sist];
                            sistemaPredominante = sist;
                        }}
                    }});

                    filas.push({{
                        eq: eq, dmPct: dmPct, inop: inop, fallas: fallas,
                        mtbf: mtbf, mttr: mttr, sistemaPredominante: sistemaPredominante,
                        fallaEnCurso: kpisDinamicos.fallaEnCurso
                    }});
                }});

                // Top Offenders: mayores horas de inoperatividad (excluye ceros)
                let ordenPorInop = [...filas].filter(f => f.inop > 0).sort((a, b) => b.inop - a.inop);
                let topOffenderSet = new Set(ordenPorInop.slice(0, 3).map(f => f.eq.equipo));

                let html = '';
                filas.forEach(f => {{
                    // Sin dato oficial en la hoja KPIs para este equipo: se muestra "—" en vez de
                    // forzar un 0 o de recalcular. No participa en Cumple/Crítico ni en Top Ofensor.
                    let sinDato = f.dmPct == null || f.mtbf == null || f.mttr == null;

                    let brecha = sinDato ? null : (f.dmPct - f.eq.dm_meta).toFixed(1);
                    let cumple = !sinDato && f.dmPct >= f.eq.dm_meta;
                    let badgeClass = cumple ? 'badge-ok' : 'badge-danger';
                    let badgeText = sinDato ? 'SIN DATO' : (cumple ? 'CUMPLE' : 'CRÍTICO');
                    let esOffender = topOffenderSet.has(f.eq.equipo);
                    // Semaforización de alertas (Requerimiento 4): DM por debajo del piso operativo
                    // (85%) o MTTR por encima de la mediana de flota (MATRIZ_MEDIANAS, la misma
                    // referencia ya usada como límite en la Matriz de Criticidad).
                    let alertaCritica = !sinDato && (f.dmPct < 85 || f.mttr > MATRIZ_MEDIANAS.mttr);
                    let rowClass = (!sinDato && !cumple) || esOffender ? 'row-critical' : '';

                    let catKey = (f.eq.categoria || '').toUpperCase();
                    let pillClass = catKey === 'CLIENTE' ? 'pill-cliente' : (catKey === 'ALQUILADOS' ? 'pill-alquilados' : 'pill-contrato');

                    let dmColor = sinDato ? 'var(--muted)' : (cumple ? 'var(--ok)' : (f.dmPct < 85 ? 'var(--critical)' : 'var(--warning)'));

                    // Dos badges INDEPENDIENTES, pueden coexistir en la misma fila:
                    // - "CALC.": este equipo no tiene fila oficial en KPIs (típicamente flota
                    //   Cliente) — solo informativo, ya que ahora %DM/MTBF/MTTR/Fallas se
                    //   recalculan en vivo para TODO equipo (ver `calcularKpisDinamico`).
                    // - "FALLA EN CURSO": el rango DESDE/HASTA actual incluye una intervención
                    //   correctiva sin Fecha/Hora Fin de Entrega Real (todavía en curso) —
                    //   calculado en vivo junto con el resto de la fila.
                    let badgeCalc = f.eq.es_calculo_dinamico
                        ? '<span class="badge ms-1" style="background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid var(--cyan); font-weight:700;" title="Este equipo no tiene fila oficial en la hoja KPIs (flota Cliente / sin meta contractual precargada)"><i class="fa-solid fa-calculator"></i> CALC.</span>'
                        : '';
                    let badgeFallaCurso = f.fallaEnCurso
                        ? '<span class="badge ms-1" style="background:rgba(220,38,38,0.15); color:#f87171; border:1px solid var(--critical); font-weight:700;" title="Intervención correctiva sin Fecha/Hora Fin de Entrega Real dentro del rango seleccionado — se contó hasta el momento actual"><i class="fa-solid fa-triangle-exclamation"></i> FALLA EN CURSO</span>'
                        : '';

                    html += `<tr class="${{rowClass}}" data-equipo="${{f.eq.equipo.toLowerCase()}}">
                        <td><span class="pill-categoria ${{pillClass}}">${{f.eq.categoria}}</span></td>
                        <td class="col-equipo">
                            <span class="badge-equipo" style="cursor:pointer;" onclick="activarFiltroEquipo('${{f.eq.equipo}}')" title="Clic para filtrar todo el dashboard por este equipo">${{f.eq.equipo}}</span>
                            ${{badgeCalc}}
                            ${{badgeFallaCurso}}
                            ${{esOffender ? '<span class="badge badge-offender ms-1"><i class="fa-solid fa-fire"></i> TOP</span>' : ''}}
                            ${{alertaCritica ? '<span class="badge badge-alert ms-1" title="DM < 85% y/o MTTR > mediana de flota"><i class="fa-solid fa-triangle-exclamation"></i> ALERTA</span>' : ''}}
                        </td>
                        <td class="dm-cell">
                            <span class="fw-bold" style="color:${{dmColor}};">${{sinDato ? '—' : f.dmPct.toFixed(1) + '%'}}</span>
                            <div class="dm-bar-track"><div class="dm-bar-fill" style="width:${{sinDato ? 0 : Math.min(100, f.dmPct)}}%; background:${{dmColor}};"></div></div>
                        </td>
                        <td>${{f.eq.dm_meta.toFixed(1)}}%</td>
                        <td class="${{sinDato ? '' : (brecha >= 0 ? 'brecha-pos' : 'brecha-neg')}}">${{sinDato ? '—' : (brecha > 0 ? '+' : '') + brecha + '%'}}</td>
                        <td>${{sinDato ? '—' : f.mtbf.toFixed(1) + ' h'}}</td>
                        <td>${{sinDato ? '—' : f.mttr.toFixed(1) + ' h'}}</td>
                        <td>${{f.fallas != null ? f.fallas : '—'}}</td>
                        <td><span class="badge ${{badgeClass}}"><span class="led-dot ${{sinDato ? '' : (cumple ? 'led-green' : 'led-red')}}"></span>${{badgeText}}</span></td>
                    </tr>`;
                }});

                tbody.innerHTML = html;
                filasCalculadasCache = filas;

                recalcularKPIsGlobales(filas);

                // Todos estos gráficos se recalculan con el MISMO universo filtrado (Tipo de
                // Flota/Equipo/Rango de Fechas) que la tabla, así quedan siempre sincronizados
                // con cualquier cambio en los filtros globales superiores.
                renderKpisPorEquipoChart(filas);
                renderTopOfensores(filas, intervencionesFiltradas, dInicioFiltro, dFinFiltro);
                renderDMChart(filas);
                renderParetoChart(equiposAMostrar, dInicioFiltro, dFinFiltro);

                const buscador = document.getElementById('buscadorEquipo');
                if (buscador && buscador.value) {{ filtrarBusqueda(buscador.value); }}
            }}

            function recalcularKPIsGlobales(filas) {{
                if (!filas || filas.length === 0) {{
                    document.getElementById('kpiDMGlobal').innerText = '0.0%';
                    document.getElementById('kpiMTBFGlobal').innerHTML = '0.0 <span class="fs-6">h</span>';
                    document.getElementById('kpiMTTRGlobal').innerHTML = '0.0 <span class="fs-6">h</span>';
                    document.getElementById('kpiFueraMeta').innerHTML = '0 <span class="fs-6">equipos</span>';
                    document.getElementById('kpiFallasGlobal').innerText = '0 fallas registradas';
                    document.getElementById('kpiDMGlobalSub').innerText = 'Sin datos para el filtro actual';
                    actualizarBadgesYSparklineKPI();
                    renderGauge(0, 0, 0);
                    return;
                }}

                // Equipos sin fila oficial en la hoja KPIs (dmPct/mtbf/mttr/fallas === null) se
                // excluyen de los promedios de flota en vez de contarse como 0 — no hay dato,
                // no se fuerza un valor.
                let filasConDato = filas.filter(f => f.dmPct != null && f.mtbf != null && f.mttr != null && f.fallas != null);

                let dmProm = filasConDato.length > 0 ? filasConDato.reduce((acc, f) => acc + f.dmPct, 0) / filasConDato.length : 0;
                let metaProm = filasConDato.length > 0 ? filasConDato.reduce((acc, f) => acc + f.eq.dm_meta, 0) / filasConDato.length : 0;
                let totalFallas = filasConDato.reduce((acc, f) => acc + f.fallas, 0);
                let totalOperativas = filasConDato.reduce((acc, f) => acc + Math.max(0, f.mtbf * f.fallas), 0);
                let totalInop = filasConDato.reduce((acc, f) => acc + (f.mttr * f.fallas), 0);

                let mtbfGlobal = totalFallas > 0 ? (totalOperativas / totalFallas) : 0;
                let mttrGlobal = totalFallas > 0 ? (totalInop / totalFallas) : 0;
                let fueraMeta = filasConDato.filter(f => f.dmPct < f.eq.dm_meta).length;

                document.getElementById('kpiDMGlobal').innerText = dmProm.toFixed(1) + '%';
                document.getElementById('kpiMTBFGlobal').innerHTML = mtbfGlobal.toFixed(1) + ' <span class="fs-6">h</span>';
                document.getElementById('kpiMTTRGlobal').innerHTML = mttrGlobal.toFixed(1) + ' <span class="fs-6">h</span>';
                document.getElementById('kpiFueraMeta').innerHTML = fueraMeta + ' <span class="fs-6">equipos</span>';
                document.getElementById('kpiFallasGlobal').innerText = totalFallas + ' fallas registradas';
                document.getElementById('kpiDMGlobalSub').innerText = filas.length + ' equipo(s) en el filtro actual';
                actualizarBadgesYSparklineKPI();
                // Velocímetro DM Global: MISMOS dmProm/metaProm/n que la tarjeta KPI de
                // arriba — una sola fuente, coincidencia exacta garantizada (Requerimiento 1).
                renderGauge(dmProm, metaProm, filasConDato.length);
            }}

            // ============================================================
            // Barra de filtros del bloque KPI superior (DM Global / MTBF Flota /
            // MTTR Flota). Comparte estado con los filtros de la tabla — NO hay dos
            // fuentes de verdad: esta barra solo escribe en los mismos controles
            // (#selectFiltroSemana, #fechaInicio/#fechaFin, #selectFiltroGrupo) y
            // dispara el MISMO `aplicarFiltrosTabla` ya validado. La sincronización
            // inversa (cambios hechos directo en la tabla) se resuelve aquí mismo,
            // en `actualizarBadgesYSparklineKPI`, invocada desde
            // `recalcularKPIsGlobales` en CADA recálculo sin importar el origen.
            // ============================================================
            function sincronizarFiltrosKPISuperiores() {{
                const selectSemanaTabla = document.getElementById('selectFiltroSemana');
                const fechaInicioTabla = document.getElementById('fechaInicio');
                const fechaFinTabla = document.getElementById('fechaFin');

                // Periodo = siempre rango de fechas explícito (fechaInicioKPI/fechaFinKPI):
                // ya no hay modo "Semanal"/"Mensual" que elegir.
                if (selectSemanaTabla) selectSemanaTabla.value = 'ALL';
                if (fechaInicioTabla) fechaInicioTabla.value = document.getElementById('fechaInicioKPI').value;
                if (fechaFinTabla) fechaFinTabla.value = document.getElementById('fechaFinKPI').value;

                const grupoTabla = document.getElementById('selectFiltroGrupo');
                if (grupoTabla) grupoTabla.value = document.getElementById('selectFlotaKPI').value;

                aplicarFiltrosTabla('header-kpi');
            }}

            function generarSparklineSvgJS(valores, color, width, height) {{
                width = width || 100; height = height || 28;
                if (!valores || valores.length < 2) {{
                    return '<span style="font-size:0.68rem;color:#64748b;">Sin histórico suficiente</span>';
                }}
                const vMin = Math.min(...valores), vMax = Math.max(...valores);
                const rango = (vMax - vMin) || 1;
                const n = valores.length, pad = 3;
                const puntos = valores.map((v, idx) => {{
                    const x = pad + (idx / (n - 1)) * (width - 2 * pad);
                    const y = height - pad - ((v - vMin) / rango) * (height - 2 * pad);
                    return [x.toFixed(1), y.toFixed(1)];
                }});
                const puntosStr = puntos.map(p => p.join(',')).join(' ');
                const [ultimoX, ultimoY] = puntos[puntos.length - 1];
                return `<svg class="kpi-sparkline" width="${{width}}" height="${{height}}" viewBox="0 0 ${{width}} ${{height}}" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="${{puntosStr}}" fill="none" stroke="${{color}}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" />
                    <circle cx="${{ultimoX}}" cy="${{ultimoY}}" r="2.6" fill="${{color}}" />
                </svg>`;
            }}

            function actualizarBadgesYSparklineKPI() {{
                const grupoTabla = document.getElementById('selectFiltroGrupo');
                const categoria = grupoTabla ? grupoTabla.value : 'ALL';

                // Mantiene el selector de Flota de la barra KPI sincronizado si el cambio
                // vino de la tabla (o de otro filtro cruzado) en vez de esta barra.
                const flotaKPI = document.getElementById('selectFlotaKPI');
                if (flotaKPI && flotaKPI.value !== categoria) flotaKPI.value = categoria;

                // Sparkline reactivo: redibuja con la serie semanal precalculada de la
                // categoría de flota activa (ilustrativa, ver `calcular_tendencia_semanal_flota`).
                const wrap = document.getElementById('sparklineDMWrap');
                if (wrap) {{
                    const serie = TENDENCIAS_POR_CATEGORIA[categoria] || TENDENCIAS_POR_CATEGORIA['ALL'];
                    wrap.innerHTML = generarSparklineSvgJS(serie ? serie.dm : [], '#38bdf8');
                }}
            }}

            // ============================================================
            // REQUERIMIENTO 1: Gráfico combinado "KPIs por Equipo"
            // Disponibilidad Física (línea) + Meta promedio del filtro (línea de
            // referencia) en el eje izquierdo; MTTR/MTBF (barras) en el eje derecho.
            // Se recalcula con el mismo universo filtrado que la tabla (Cliente/
            // Tipo de Flota, Semana, Rango de Fechas). NOTA: no incluye "Utilización"
            // — esa métrica no existe en el Excel de origen (no hay horas operadas vs.
            // horas disponibles) y agregarla habría significado inventar un dato.
            // ============================================================
            function renderKpisPorEquipoChart(filas) {{
                const wrap = document.getElementById('chartKpisEquipoWrap');
                if (!filas || filas.length === 0) {{
                    Plotly.react('chartKpisEquipo', [], {{
                        template: 'plotly_dark', paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                        annotations: [{{ text: 'Sin datos para el filtro actual', showarrow: false, font: {{ color: '#64748b' }} }}],
                        height: 300
                    }}, {{ displaylogo: false, responsive: true }});
                    return;
                }}

                const ordenadas = [...filas].sort((a, b) => a.eq.equipo.localeCompare(b.eq.equipo));
                const equipos = ordenadas.map(f => f.eq.equipo);
                const metaProm = ordenadas.reduce((acc, f) => acc + f.eq.dm_meta, 0) / ordenadas.length;

                const traceMTTR = {{
                    type: 'bar', name: 'MTTR (h)', yaxis: 'y2',
                    x: equipos, y: ordenadas.map(f => f.mttr),
                    marker: {{ color: '#f7931e' }},
                    hovertemplate: '<b>%{{x}}</b><br>MTTR: %{{y:.1f}} h<extra></extra>'
                }};
                const traceMTBF = {{
                    type: 'bar', name: 'MTBF (h)', yaxis: 'y2',
                    x: equipos, y: ordenadas.map(f => f.mtbf),
                    marker: {{ color: '#93c5fd' }},
                    hovertemplate: '<b>%{{x}}</b><br>MTBF: %{{y:.1f}} h<extra></extra>'
                }};
                const traceDisponibilidad = {{
                    type: 'scatter', mode: 'lines+markers', name: 'Disponibilidad Física (%)',
                    x: equipos, y: ordenadas.map(f => f.dmPct),
                    line: {{ color: '#38bdf8', width: 2.5 }},
                    marker: {{ size: 6, color: '#38bdf8' }},
                    hovertemplate: '<b>%{{x}}</b><br>Disponibilidad: %{{y:.1f}}%<extra></extra>'
                }};

                const layout = {{
                    template: 'plotly_dark',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ family: 'Inter, Segoe UI, sans-serif', color: '#e2e8f0' }},
                    hoverlabel: {{ bgcolor: 'rgba(21,28,44,0.95)', bordercolor: '#38bdf8', font: {{ family: 'JetBrains Mono, monospace', size: 12, color: '#f8fafc' }} }},
                    barmode: 'group',
                    xaxis: {{ tickangle: -45, gridcolor: 'rgba(148,163,184,0.08)' }},
                    yaxis: {{ title: '%', range: [0, 110], gridcolor: 'rgba(148,163,184,0.12)' }},
                    yaxis2: {{ title: 'Horas', overlaying: 'y', side: 'right', showgrid: false }},
                    legend: {{ orientation: 'h', yanchor: 'bottom', y: 1.08, xanchor: 'center', x: 0.5 }},
                    margin: {{ l: 50, r: 50, t: 30, b: 90 }},
                    height: 460,
                    shapes: [{{
                        type: 'line', x0: 0, x1: 1, xref: 'paper', y0: metaProm, y1: metaProm, yref: 'y',
                        line: {{ color: '#dc2626', width: 2, dash: 'dash' }}
                    }}],
                    annotations: [{{
                        x: 1, y: metaProm, xref: 'paper', yref: 'y', xanchor: 'left', yanchor: 'bottom',
                        text: 'Meta ' + metaProm.toFixed(1) + '%', showarrow: false,
                        font: {{ color: '#dc2626', size: 11 }}
                    }}]
                }};

                if (wrap) {{ wrap.style.minWidth = Math.max(900, equipos.length * 42) + 'px'; }}
                Plotly.react('chartKpisEquipo', [traceMTTR, traceMTBF, traceDisponibilidad], layout, {{ displaylogo: false, responsive: true }});

                const gdKpisEq = document.getElementById('chartKpisEquipo');
                gdKpisEq.removeAllListeners && gdKpisEq.removeAllListeners('plotly_click');
                gdKpisEq.on('plotly_click', function(evt) {{
                    if (!evt || !evt.points || !evt.points.length) return;
                    activarFiltroEquipo(evt.points[0].x);
                }});
            }}

            // ============================================================
            // REQUERIMIENTO 2: Top Ofensores — equipos con mayor pérdida de
            // disponibilidad (horas de parada) dentro del filtro actual.
            // "Tendencia" compara el %DM del equipo en el rango filtrado contra un
            // rango inmediatamente anterior de igual duración (misma fórmula oficial
            // de fusión de intervalos), usando el historial COMPLETO de intervenciones
            // (no acotado por el filtro de Semana) para poder mirar "hacia atrás".
            // ============================================================
            function renderTopOfensores(filas, intervencionesFiltradas, dInicioFiltro, dFinFiltro) {{
                const tbody = document.getElementById('tbodyTopOfensores');
                if (!tbody) return;

                const ofensores = [...filas].filter(f => f.inop > 0).sort((a, b) => b.inop - a.inop).slice(0, 8);

                if (ofensores.length === 0) {{
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-secondary py-3">Sin horas de parada registradas para el filtro actual</td></tr>';
                    return;
                }}

                const msPeriodo = dFinFiltro - dInicioFiltro;
                const dInicioPrev = new Date(dInicioFiltro.getTime() - msPeriodo);
                const dFinPrev = new Date(dInicioFiltro.getTime());
                const horasPeriodoPrev = Math.max(0, msPeriodo / (1000 * 3600));

                let html = '';
                ofensores.forEach(f => {{
                    const subsPrev = rawIntervenciones.filter(i => i.equipo === f.eq.equipo);
                    const inopPrev = calcularHorasInopExactas(subsPrev, dInicioPrev, dFinPrev);
                    const dmPctPrev = horasPeriodoPrev > 0
                        ? Math.max(0, Math.min(100, ((horasPeriodoPrev - inopPrev) / horasPeriodoPrev) * 100))
                        : f.dmPct;

                    const deltaPP = f.dmPct - dmPctPrev;
                    const mejorando = deltaPP >= 0;
                    const tendenciaIcon = mejorando ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down';
                    const tendenciaClass = mejorando ? 'kpi-trend-up' : 'kpi-trend-down';

                    const cumple = f.dmPct >= f.eq.dm_meta;
                    const alertaCritica = f.dmPct < 85 || f.mttr > MATRIZ_MEDIANAS.mttr;
                    const estatusClass = cumple ? 'badge-ok' : 'badge-danger';
                    const estatusText = cumple ? 'CUMPLE' : 'CRÍTICO';

                    html += `<tr class="${{alertaCritica ? 'row-critical' : ''}}">
                        <td><span class="badge-equipo" style="cursor:pointer;" onclick="activarFiltroEquipo('${{f.eq.equipo}}')" title="Clic para filtrar todo el dashboard por este equipo">${{f.eq.equipo}}</span></td>
                        <td class="fw-bold" style="color:var(--critical);">${{f.inop.toFixed(1)}} h</td>
                        <td>${{f.sistemaPredominante || '—'}}</td>
                        <td>
                            <span class="badge ${{estatusClass}}"><span class="led-dot ${{cumple ? 'led-green' : 'led-red'}}"></span>${{estatusText}}</span>
                            ${{alertaCritica ? '<span class="badge badge-alert ms-1"><i class="fa-solid fa-triangle-exclamation"></i></span>' : ''}}
                        </td>
                        <td><span class="kpi-trend ${{tendenciaClass}}"><i class="fa-solid ${{tendenciaIcon}}"></i> ${{deltaPP >= 0 ? '+' : ''}}${{deltaPP.toFixed(1)}} pp vs. periodo anterior</span></td>
                    </tr>`;
                }});

                tbody.innerHTML = html;
            }}

            function aplicarFiltrosTabla(origen) {{
                const selectGrupo = document.getElementById('selectFiltroGrupo').value;
                const selectEquipo = document.getElementById('selectFiltroEquipo').value;
                const fIniVal = document.getElementById('fechaInicio').value;
                const fFinVal = document.getElementById('fechaFin').value;

                let dInicio = new Date(fIniVal + "T00:00:00");
                let dFin = new Date(fFinVal + "T23:59:59");

                let intervencionesFiltradas = rawIntervenciones;
                // Cross-filtering por sistema (clic en una barra del Pareto): solo se consideran
                // como "inoperativas" las intervenciones del sistema seleccionado. La fórmula de
                // %DM no cambia — solo el universo de intervenciones que alimenta el numerador.
                if (filtroSistemaActivo) {{
                    intervencionesFiltradas = intervencionesFiltradas.filter(i => (i.sistema || '').toUpperCase() === filtroSistemaActivo.toUpperCase());
                }}

                let msPeriodo = dFin - dInicio;
                let horasPeriodo = Math.max(0, msPeriodo / (1000 * 3600));

                // %DM/MTBF/MTTR/Fallas de la tabla YA NO dependen del rango de fechas DESDE/HASTA
                // (ver renderizarTabla): siempre son el KPI OFICIAL de la hoja "KPIs". dInicio/dFin/
                // horasPeriodo se siguen pasando solo para las vistas auxiliares (Top Ofensores,
                // Sistema Predominante), que sí usan el Registro de Intervenciones acotado al rango.
                renderizarTabla(intervencionesFiltradas, dInicio, dFin, horasPeriodo, selectEquipo, selectGrupo);
            }}

            function limpiarFiltros() {{
                document.getElementById('selectFiltroGrupo').value = 'ALL';
                document.getElementById('selectFiltroEquipo').value = 'ALL';
                filtroEquipoActivo = null;
                filtroSistemaActivo = null;
                mostrarChipFiltro();
                aplicarFiltrosTabla('reset');
            }}

            function exportarCSV() {{
                if (!filasCalculadasCache || filasCalculadasCache.length === 0) {{
                    alert('No hay datos para exportar con el filtro actual.');
                    return;
                }}
                let encabezado = ['GRUPO','EQUIPO','%DM','DM_META','BRECHA','MTBF_h','MTTR_h','FALLAS','ESTADO'];
                let filasCSV = filasCalculadasCache.map(f => {{
                    let cumple = f.dmPct >= f.eq.dm_meta;
                    return [
                        f.eq.categoria, f.eq.equipo, f.dmPct.toFixed(1), f.eq.dm_meta.toFixed(1),
                        (f.dmPct - f.eq.dm_meta).toFixed(1), f.mtbf.toFixed(1), f.mttr.toFixed(1),
                        f.fallas, cumple ? 'CUMPLE' : 'CRITICO'
                    ].join(',');
                }});
                let contenido = [encabezado.join(','), ...filasCSV].join('\\n');
                let blob = new Blob(["\\ufeff" + contenido], {{ type: 'text/csv;charset=utf-8;' }});
                let url = URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = 'confiabilidad_flota_filtrado.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}

            // Exportar a Excel sin depender de ninguna librería externa: se construye una
            // tabla HTML y se sirve con MIME/extensión .xls — Excel la abre nativamente
            // (técnica estándar para exportar sin sumar dependencias al HTML autocontenido).
            function exportarExcel() {{
                if (!filasCalculadasCache || filasCalculadasCache.length === 0) {{
                    alert('No hay datos para exportar con el filtro actual.');
                    return;
                }}
                let filasHtml = filasCalculadasCache.map(f => {{
                    let cumple = f.dmPct >= f.eq.dm_meta;
                    return `<tr>
                        <td>${{f.eq.categoria}}</td>
                        <td>${{f.eq.equipo}}</td>
                        <td>${{f.dmPct.toFixed(1)}}</td>
                        <td>${{f.eq.dm_meta.toFixed(1)}}</td>
                        <td>${{(f.dmPct - f.eq.dm_meta).toFixed(1)}}</td>
                        <td>${{f.mtbf.toFixed(1)}}</td>
                        <td>${{f.mttr.toFixed(1)}}</td>
                        <td>${{f.fallas}}</td>
                        <td>${{f.inop.toFixed(1)}}</td>
                        <td>${{f.sistemaPredominante || ''}}</td>
                        <td>${{cumple ? 'CUMPLE' : 'CRITICO'}}</td>
                    </tr>`;
                }}).join('');

                let tablaHtml = `<table border="1">
                    <thead><tr>
                        <th>GRUPO</th><th>EQUIPO</th><th>%DM</th><th>DM_META</th><th>BRECHA</th>
                        <th>MTBF_h</th><th>MTTR_h</th><th>FALLAS</th><th>HORAS_PARADA</th>
                        <th>TIPO_FALLA_PREDOMINANTE</th><th>ESTADO</th>
                    </tr></thead>
                    <tbody>${{filasHtml}}</tbody>
                </table>`;

                let documento = `<html xmlns:x="urn:schemas-microsoft-com:office:excel">
                    <head><meta charset="UTF-8"><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet>
                    <x:Name>Confiabilidad Flota</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions>
                    </x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head>
                    <body>${{tablaHtml}}</body>
                </html>`;

                let blob = new Blob([documento], {{ type: 'application/vnd.ms-excel' }});
                let url = URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = 'confiabilidad_flota_filtrado.xls';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}

            function filtrarBusqueda(texto) {{
                const t = (texto || '').toLowerCase().trim();
                const filas = document.querySelectorAll('#tbodyKPIs tr');
                filas.forEach(tr => {{
                    const eq = tr.getAttribute('data-equipo') || '';
                    tr.style.display = (t === '' || eq.includes(t)) ? '' : 'none';
                }});
            }}

            let ordenActual = {{ col: null, asc: true }};

            function ordenarTabla(colIndex, tipo) {{
                const tbody = document.getElementById('tbodyKPIs');
                const filas = Array.from(tbody.querySelectorAll('tr'));

                if (ordenActual.col === colIndex) {{
                    ordenActual.asc = !ordenActual.asc;
                }} else {{
                    ordenActual = {{ col: colIndex, asc: true }};
                }}

                filas.sort((a, b) => {{
                    let va = a.children[colIndex].innerText.trim();
                    let vb = b.children[colIndex].innerText.trim();

                    if (tipo === 'num') {{
                        va = parseFloat(va.replace(/[^0-9\\.\\-]/g, '')) || 0;
                        vb = parseFloat(vb.replace(/[^0-9\\.\\-]/g, '')) || 0;
                        return ordenActual.asc ? va - vb : vb - va;
                    }}
                    return ordenActual.asc ? va.localeCompare(vb) : vb.localeCompare(va);
                }});

                filas.forEach(tr => tbody.appendChild(tr));
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                // DM vs. Meta y Pareto de Sistemas ya no se disparan aparte: quedan dentro de
                // la cascada de `aplicarFiltrosTabla('init')` -> `renderizarTabla`, con el
                // mismo universo filtrado (Flota/Equipo/Fecha) que la tabla y las tarjetas KPI.
                aplicarFiltrosTabla('init');
                actualizarKpiPM(document.getElementById('selectSemanaPM').value);
                renderDonutChart(document.getElementById('selectSemanaDonut').value);
                renderMatrixChart();
                // El Velocímetro DM Global ya no se dispara aparte: `aplicarFiltrosTabla('init')`
                // arriba cascadea a `recalcularKPIsGlobales`, que llama a `renderGauge` con los
                // mismos valores que las tarjetas KPI superiores.
                renderOtrosChart(document.getElementById('selectSemanaOtros').value);

                // chartPMDesviacion es una figura estática de Python (Plotly.newPlot ya
                // embebido en el HTML) que solo se restyla/relayout-ea por semana — el div
                // no se recrea, así que el listener de clic se ata UNA sola vez aquí.
                const gdPM = document.getElementById('chartPMDesviacion');
                if (gdPM) {{
                    gdPM.on('plotly_click', function(evt) {{
                        if (!evt || !evt.points || !evt.points.length) return;
                        activarFiltroEquipo(evt.points[0].x);
                    }});
                }}
            }});
        </script>

        {mtbs_script_html}

        {bkl_cards_script_html}

        {efd_script_html}
    </body>
    </html>
    """

    path_salida = Path(ARCHIVO_SALIDA_HTML)
    path_salida.write_text(html_template, encoding="utf-8")
    print(f"✅ Dashboard generado exitosamente en: {path_salida.absolute()}")
    try:
        webbrowser.open(path_salida.resolve().as_uri())
    except Exception:
        print("ℹ️  No se pudo abrir el navegador automáticamente. Abra el archivo HTML manualmente.")


# ==============================================================================
# D. MÓDULO INDEPENDIENTE — MTBS (MEAN TIME BETWEEN SERVICING) · FLOTA VOLVO FMX
# ==============================================================================
# REGLA DE ORO: este bloque es un módulo AISLADO. No modifica, referencia ni
# depende de ninguna función, variable, tabla o gráfico de MTBF/MTTR/Disponibilidad
# Mecánica/Pareto de Fallas de las secciones A-C de este archivo. Es la traducción
# a Python/pandas de la vista SQL de referencia `vw_mtbs_volvo_fmx`:
#
#   CREATE OR REPLACE VIEW vw_mtbs_volvo_fmx AS
#   SELECT codigo_equipo, DATE_TRUNC('month', fecha_inicio_evento) AS mes_operativo,
#          SUM(horas_operativas) AS horas_operativas_totales,
#          COUNT(CASE WHEN duracion_horas > 0 AND tipo_evento IN ('PM','CM')
#                     THEN id_evento END) AS total_intervenciones,
#          SUM(horas_operativas) / NULLIF(COUNT(...), 0) AS mtbs_horas
#   FROM Fact_Eventos_Taller E JOIN Fact_Horas_Equipos H ON ...
#   WHERE E.flota = 'Volvo FMX'
#   GROUP BY codigo_equipo, mes_operativo
#
# Este repositorio no tiene motor SQL ni tablas Fact_Eventos_Taller/Fact_Horas_
# Equipos: la fuente real es el mismo Excel ya cargado por `cargar_intervenciones`
# / `cargar_parque_equipos` (secciones A), consumido aquí SOLO COMO LECTURA — sin
# tocar esas funciones.
#
# ACTUALIZACIÓN — Fact_Horas_Equipos real (horómetros Volvo Connect): se integran
# los 3 reportes mensuales "Rendimiento" de mayo/junio/julio 2026 (columna 'Tiempo
# total (hh:mm)' = horas motor reales del periodo; 'Uso del vehículo (%)' = %
# Utilización real) como la fuente PREFERIDA de horas operativas para MTBS
# mensual. El código de equipo del reporte ('ANT CV-474 E623927') se normaliza a
# 'CV-00474' vía zero-padding — se probó y confirmó 100% de coincidencia (126/126
# filas) contra COD INTERNO; el chasis NO se usa como llave porque el Excel de
# PARQUE DE EQUIPOS tiene chasis con un prefijo 'EE' duplicado por error de tipeo
# en varias filas. Cuando un equipo/mes no tiene horómetro real disponible (fuera
# de mayo-julio 2026, o equipo ausente del reporte), se usa como respaldo la
# aproximación por fusión de intervalos (horas-calendario menos horas de taller,
# con `_mtbs_fusionar_intervalos`, propia e independiente de cualquier otro
# cálculo del archivo) — cada fila queda marcada con su `fuente_horas` para que
# la UI lo deje explícito.
#
# HALLAZGO DE DATOS: el Excel de intervenciones de taller (Registro de
# Intervenciones) NO tiene registros anteriores al 19 de junio de 2026 — mayo
# 2026 tiene horas de horómetro reales pero CERO intervenciones registradas, por
# lo que el MTBS de mayo queda indefinido (numerador real, denominador vacío) y
# se muestra así explícitamente, sin inventar un valor.
# ==============================================================================


def _mtbs_parsear_codigo_vehiculo(texto_vehiculo: str):
    """Extrae y normaliza el código de equipo desde la etiqueta de vehículo de un
    reporte Volvo Connect, p.ej. 'ANT CV-474 E623927' -> 'CV-00474'. Búsqueda NO
    anclada a una posición fija de token (\\b[A-Za-z]{{2}}-0*\\d+) para tolerar los
    formatos inconsistentes de las distintas operaciones/sitios que comparten la
    misma cuenta Volvo Connect (p.ej. 'SHA:CV-00434:RE938671', 'QLL CV-431E939100',
    sin espacios ni con separadores ':'). Confirmado 100% de coincidencia (126/126
    filas del reporte de horómetros de mayo-julio + 44/44 filas 'ANT' del reporte
    multi-sitio de abril) contra COD INTERNO de PARQUE DE EQUIPOS — más confiable
    que emparejar por chasis (que tiene inconsistencias de tipeo en el Excel de
    origen, p.ej. 'EE623927' en vez de 'E623927')."""
    m = re.search(r"\b([A-Za-z]{2})-0*(\d+)", str(texto_vehiculo))
    if not m:
        return None
    prefijo, numero = m.group(1).upper(), m.group(2)
    return f"{prefijo}-{int(numero):05d}"


def _mtbs_hhmm_a_horas(valor) -> float:
    """Convierte un valor 'hh:mm' (puede superar 24h, p.ej. '489:34') del reporte
    de horómetros a horas decimales. Devuelve 0.0 si no es parseable. Utilidad
    privada y exclusiva del módulo MTBS."""
    if pd.isna(valor):
        return 0.0
    texto = str(valor).strip()
    if ":" not in texto:
        try:
            return float(texto)
        except ValueError:
            return 0.0
    try:
        horas_str, minutos_str = texto.split(":")
        return abs(int(horas_str)) + int(minutos_str) / 60.0
    except (ValueError, IndexError):
        return 0.0


def cargar_horometros_mensual(ruta: str, periodo: str) -> pd.DataFrame:
    """
    Lee un reporte mensual "Rendimiento" de Volvo Connect (hoja 'Datos del
    informe') y devuelve, por equipo: horas operativas reales del horómetro
    ('Tiempo total') y % de utilización real ('Uso del vehículo'). Lectura
    tolerante a fallos: si el archivo no existe o no tiene el formato esperado,
    devuelve un DataFrame vacío y emite un aviso — nunca detiene la generación
    del resto del dashboard.
    """
    columnas_salida = ["codigo_equipo", "periodo", "horas_operativas_horometro", "pct_utilizacion"]
    try:
        df = pd.read_excel(ruta, sheet_name="Datos del informe", header=1)
    except Exception as e:
        print(f"⚠️  Aviso (módulo MTBS): no se pudo leer el horómetro de {periodo} ({ruta}): {e}")
        return pd.DataFrame(columns=columnas_salida)

    df.columns = [str(c).strip() for c in df.columns]
    if "Vehículos" not in df.columns or "Tiempo total (hh:mm)" not in df.columns:
        print(f"⚠️  Aviso (módulo MTBS): el horómetro de {periodo} no tiene las columnas esperadas. Se omite.")
        return pd.DataFrame(columns=columnas_salida)

    df = df[df["Vehículos"].notna() & (df["Vehículos"].astype(str).str.strip() != "Todo:")].copy()

    df["codigo_equipo"] = df["Vehículos"].apply(_mtbs_parsear_codigo_vehiculo)
    df = df.dropna(subset=["codigo_equipo"]).copy()

    df["horas_operativas_horometro"] = df["Tiempo total (hh:mm)"].apply(_mtbs_hhmm_a_horas)
    df["pct_utilizacion"] = pd.to_numeric(df.get("Uso del vehículo (%)"), errors="coerce")
    df["periodo"] = periodo

    return df[columnas_salida].reset_index(drop=True)


def cargar_horometros_consolidado() -> pd.DataFrame:
    """Consolida los 3 reportes mensuales de horómetros (mayo/junio/julio 2026) en
    un único DataFrame [codigo_equipo, periodo, horas_operativas_horometro,
    pct_utilizacion]. Fuente EXCLUSIVA del módulo MTBS."""
    partes = [
        cargar_horometros_mensual(RUTA_HOROMETROS_MAYO, "2026-05"),
        cargar_horometros_mensual(RUTA_HOROMETROS_JUNIO, "2026-06"),
        cargar_horometros_mensual(RUTA_HOROMETROS_JULIO, "2026-07"),
    ]
    partes_validas = [p for p in partes if len(p)]
    if not partes_validas:
        return pd.DataFrame(columns=["codigo_equipo", "periodo", "horas_operativas_horometro", "pct_utilizacion"])
    return pd.concat(partes_validas, ignore_index=True)


def _vc_extraer_periodo_de_nombre_archivo(nombre_archivo: str):
    """Extrae el periodo AAAA-MM del nombre de un reporte Volvo Connect, p.ej.
    'ABRIL 2026.xlsx' -> '2026-04'. Devuelve None si el nombre no sigue el patrón
    'MES AAAA' (mes en español). Insensible a mayúsculas/acentos."""
    nombre = Path(nombre_archivo).stem.strip().upper()
    nombre_sin_acentos = (
        nombre.replace("Á", "A").replace("É", "E").replace("Í", "I")
        .replace("Ó", "O").replace("Ú", "U")
    )
    m = re.search(r"([A-Z]+)\s+(\d{4})", nombre_sin_acentos)
    if not m:
        return None
    mes_num = MESES_ES.get(m.group(1))
    if mes_num is None:
        return None
    return f"{m.group(2)}-{mes_num:02d}"


def cargar_reporte_volvo_connect(ruta_archivo: str, equipos_fmx: set) -> dict:
    """
    Lee UN reporte mensual Volvo Connect (multi-sitio, hoja 'Datos del informe'),
    extrae el periodo desde el nombre del archivo, aplica el INNER JOIN estricto
    contra `equipos_fmx` (WHERE flota = 'Volvo FMX', ver `_mtbs_equipos_volvo_fmx`)
    y limpia/convierte a numérico las variables de hábito operativo pedidas.

    Retorna {"periodo", "df", "total_leidos", "retenidos", "ignorados"} — nunca
    lanza excepción: un archivo ilegible o sin periodo reconocible se reporta con
    df vacío en vez de detener el resto del pipeline.
    """
    nombre_archivo = Path(ruta_archivo).name
    columnas_salida = [
        "codigo_equipo", "Periodo_Volvo", "distancia_km", "diesel_motor_marcha_l",
        "promedio_conduccion_kmh", "ralenti_pct", "pto_pct", "punto_muerto_pct",
        "programador_velocidad_pct", "consumo_l_100km", "archivo_origen"
    ]
    resultado_vacio = {"periodo": None, "df": pd.DataFrame(columns=columnas_salida),
                        "total_leidos": 0, "retenidos": 0, "ignorados": 0}

    periodo = _vc_extraer_periodo_de_nombre_archivo(nombre_archivo)
    if periodo is None:
        print(f"⚠️  Aviso (Fact_VolvoConnect): '{nombre_archivo}' no sigue el patrón 'MES AAAA' — se omite.")
        return resultado_vacio

    try:
        df = pd.read_excel(ruta_archivo, sheet_name="Datos del informe", header=1)
    except Exception as e:
        print(f"⚠️  Aviso (Fact_VolvoConnect): no se pudo leer '{nombre_archivo}' ({e}). Se omite.")
        return resultado_vacio

    df.columns = [str(c).strip() for c in df.columns]
    if "Vehículos" not in df.columns:
        print(f"⚠️  Aviso (Fact_VolvoConnect): '{nombre_archivo}' no tiene columna 'Vehículos'. Se omite.")
        return resultado_vacio

    df = df[df["Vehículos"].notna() & (df["Vehículos"].astype(str).str.strip() != "Todo:")].copy()
    total_leidos = len(df)

    # Filtro cruzado (INNER JOIN) contra la tabla maestra de equipos: solo se
    # conservan códigos que pertenecen explícitamente a la flota Volvo FMX.
    df["codigo_equipo"] = df["Vehículos"].apply(_mtbs_parsear_codigo_vehiculo)
    retenidos_df = df[df["codigo_equipo"].isin(equipos_fmx)].copy()
    ignorados = total_leidos - len(retenidos_df)

    mapa_columnas = {
        "Distancia total (km)": "distancia_km",
        "Diésel con motor en marcha (l)": "diesel_motor_marcha_l",
        "Promedio de conducción (km/h)": "promedio_conduccion_kmh",
        "Ralentí (%)": "ralenti_pct",
        "PTO (%)": "pto_pct",
        "En punto muerto (%)": "punto_muerto_pct",
        "Programador de velocidad (%)": "programador_velocidad_pct",
        "Promedio de diésel con motor en marcha (l/100\xa0km)": "consumo_l_100km",
    }
    for col_origen, col_destino in mapa_columnas.items():
        if col_origen in retenidos_df.columns:
            # Limpieza defensiva: quita '%'/texto residual (p.ej. 'N/D', '-') y
            # convierte a numérico; valores ya numéricos pasan sin cambios.
            valores = retenidos_df[col_origen].astype(str).str.replace("%", "", regex=False).str.strip()
            retenidos_df[col_destino] = pd.to_numeric(valores, errors="coerce")
        else:
            retenidos_df[col_destino] = pd.NA

    retenidos_df["Periodo_Volvo"] = periodo
    retenidos_df["archivo_origen"] = nombre_archivo

    return {
        "periodo": periodo,
        "df": retenidos_df[columnas_salida].reset_index(drop=True),
        "total_leidos": total_leidos,
        "retenidos": len(retenidos_df),
        "ignorados": ignorados,
    }


def construir_fact_volvo_connect(ruta_carpeta: str, df_parque: pd.DataFrame) -> pd.DataFrame:
    """
    ETL dinámico (Requerimientos 1-4): escanea `ruta_carpeta` en busca de TODOS
    los .xlsx presentes (sin nombres de archivo hardcodeados — cualquier
    'MES AAAA.xlsx' nuevo se procesa automáticamente), aplica el INNER JOIN
    estricto de flota Volvo FMX y consolida los registros retenidos en
    `Fact_VolvoConnect`. Imprime por consola el detalle de ignorados/retenidos por
    archivo y el total. Nunca detiene la generación del dashboard: carpeta
    ausente/vacía o archivo ilegible se reportan con aviso, no con excepción.
    """
    columnas_salida = [
        "codigo_equipo", "Periodo_Volvo", "distancia_km", "diesel_motor_marcha_l",
        "promedio_conduccion_kmh", "ralenti_pct", "pto_pct", "punto_muerto_pct",
        "programador_velocidad_pct", "consumo_l_100km", "archivo_origen"
    ]

    carpeta = Path(ruta_carpeta)
    print(f"\n📂 Fact_VolvoConnect — escaneando: {carpeta}")
    if not carpeta.exists() or not carpeta.is_dir():
        print("⚠️  Aviso (Fact_VolvoConnect): la carpeta no existe. Se omite el ETL de Volvo Connect.")
        return pd.DataFrame(columns=columnas_salida)

    archivos = sorted(carpeta.glob("*.xlsx"))
    if not archivos:
        print("⚠️  Aviso (Fact_VolvoConnect): no se encontraron archivos .xlsx en la carpeta.")
        return pd.DataFrame(columns=columnas_salida)

    equipos_fmx = _mtbs_equipos_volvo_fmx(df_parque)

    partes = []
    total_leidos_global = 0
    total_retenidos_global = 0
    total_ignorados_global = 0

    for archivo in archivos:
        r = cargar_reporte_volvo_connect(str(archivo), equipos_fmx)
        total_leidos_global += r["total_leidos"]
        total_retenidos_global += r["retenidos"]
        total_ignorados_global += r["ignorados"]
        if r["periodo"]:
            print(f"   {archivo.name:<22s} -> periodo {r['periodo']} | leídos: {r['total_leidos']:>4d} | "
                  f"retenidos (Volvo FMX): {r['retenidos']:>3d} | ignorados: {r['ignorados']:>4d}")
        if len(r["df"]):
            partes.append(r["df"])

    print(f"📊 Fact_VolvoConnect — TOTAL: {total_leidos_global} registros leídos | "
          f"{total_retenidos_global} Volvo FMX útiles retenidos | "
          f"{total_ignorados_global} ignorados (otras flotas/sitios)\n")

    if not partes:
        return pd.DataFrame(columns=columnas_salida)
    return pd.concat(partes, ignore_index=True)


def _mtbs_fusionar_intervalos(intervalos: list) -> list:
    """Fusiona intervalos [ini, fin] solapados. Utilidad privada y exclusiva del
    módulo MTBS — no se comparte con ninguna otra sección de este archivo."""
    if not intervalos:
        return []
    intervalos_ordenados = sorted(intervalos, key=lambda x: x[0])
    fusionados = [list(intervalos_ordenados[0])]
    for ini, fin in intervalos_ordenados[1:]:
        if ini <= fusionados[-1][1]:
            fusionados[-1][1] = max(fusionados[-1][1], fin)
        else:
            fusionados.append([ini, fin])
    return fusionados


def _mtbs_equipos_volvo_fmx(df_parque: pd.DataFrame) -> set:
    """WHERE E.flota = 'Volvo FMX' — set de COD INTERNO cuya MARCA es VOLVO y
    MODELO contiene 'FMX'. Único punto de verdad de este filtro, reutilizado por
    `vw_mtbs_volvo_fmx` y por el ETL de `Fact_VolvoConnect` (INNER JOIN estricto
    de flota), para no duplicar el criterio en dos lugares."""
    marca_ok = df_parque.get("MARCA", pd.Series(dtype=str)).astype(str).str.strip().str.upper() == "VOLVO"
    modelo_ok = df_parque.get("MODELO", pd.Series(dtype=str)).astype(str).str.upper().str.contains("FMX", na=False)
    return set(df_parque.loc[marca_ok & modelo_ok, "COD INTERNO"])


def vw_mtbs_volvo_fmx(df_intervenciones: pd.DataFrame, df_parque: pd.DataFrame, periodo: str = "M",
                       df_horometros: pd.DataFrame = None) -> pd.DataFrame:
    """
    MTBS = Horas Operativas Totales / N° Total de Intervenciones, agrupado por
    código de equipo Volvo FMX y por periodo.

    Parámetros
    ----------
    df_intervenciones : DataFrame ya devuelto por `cargar_intervenciones` (solo
        lectura — equivale a Fact_Eventos_Taller).
    df_parque : DataFrame ya devuelto por `cargar_parque_equipos` (solo lectura —
        se usa únicamente para resolver el WHERE flota = 'Volvo FMX' vía MARCA/
        MODELO).
    periodo : "M" mensual (equivalente a DATE_TRUNC('month', ...)) o "W" semanal
        (usa la columna SEMANA ya calculada, para no reinventar otro esquema de
        semana calendario). Los horómetros son mensuales, así que solo afinan "M".
    df_horometros : DataFrame opcional de `cargar_horometros_consolidado()`
        [codigo_equipo, periodo, horas_operativas_horometro, pct_utilizacion].
        Cuando existe una fila real para (equipo, mes), se usa como numerador
        EXACTO en vez de la aproximación por fusión de intervalos; si no, se
        conserva el respaldo aproximado. Cada fila de salida indica cuál fuente
        se usó en `fuente_horas`.

    Retorna
    -------
    DataFrame: codigo_equipo, periodo, horas_operativas_totales,
    total_intervenciones, mtbs_horas, pct_utilizacion, fuente_horas — una fila
    por equipo y periodo.
    """
    columnas_salida = [
        "codigo_equipo", "periodo", "horas_operativas_totales", "total_intervenciones",
        "mtbs_horas", "pct_utilizacion", "fuente_horas"
    ]

    # WHERE E.flota = 'Volvo FMX'
    equipos_fmx = _mtbs_equipos_volvo_fmx(df_parque)
    if not equipos_fmx:
        return pd.DataFrame(columns=columnas_salida)

    df = df_intervenciones[df_intervenciones["EQUIPO"].isin(equipos_fmx)].copy()

    # tipo_evento IN ('PM','CM') -> PREVENTIVO/CORRECTIVO ; duracion_horas > 0
    tipo_col = df.get("TIPO DE INTERVENCION", pd.Series(dtype=str)).astype(str)
    es_pm_cm = tipo_col.str.contains("PREVENTIV", na=False) | tipo_col.str.contains("CORRECTIV", na=False)
    duracion_valida = df.get("Horas_Reparacion_Neta", pd.Series(dtype=float)).fillna(0) > 0
    df_validos = df[es_pm_cm & duracion_valida].copy()

    if periodo == "W":
        df_validos["periodo_key"] = df_validos["SEMANA"]
    else:
        # Descarta filas sin FECHA ANTES de convertir a texto: dt.to_period().astype(str)
        # convierte NaT en el literal "NaT", que ya no es detectable con pd.isna() más
        # abajo y colaría como un periodo mensual fantasma.
        df_validos = df_validos[df_validos["FECHA"].notna()].copy()
        df_validos["periodo_key"] = df_validos["FECHA"].dt.to_period("M").astype(str)

    grupos_taller = {clave: grupo for clave, grupo in df_validos.groupby(["EQUIPO", "periodo_key"])}

    # Horómetro real solo aplica a la rama mensual — se indexa (equipo, periodo).
    horometro_por_clave = {}
    if periodo == "M" and df_horometros is not None and len(df_horometros):
        horometro_valido = df_horometros[df_horometros["codigo_equipo"].isin(equipos_fmx)]
        for _, r in horometro_valido.iterrows():
            horometro_por_clave[(r["codigo_equipo"], r["periodo"])] = r

    # Universo de (equipo, periodo) a calcular: todo combo con datos de TALLER
    # y/o de HORÓMETRO (así un mes solo-horómetro, como mayo, también se reporta
    # — con MTBS indefinido si no hay intervenciones — en vez de desaparecer).
    claves = set(grupos_taller.keys()) | set(horometro_por_clave.keys())

    filas = []
    for equipo, periodo_key in claves:
        if pd.isna(periodo_key):
            continue

        grupo = grupos_taller.get((equipo, periodo_key))
        total_intervenciones = int(len(grupo)) if grupo is not None else 0

        fila_horometro = horometro_por_clave.get((equipo, periodo_key))

        if periodo == "W":
            horas_calendario = 168.0
            periodo_str = str(int(periodo_key))
        else:
            horas_calendario = pd.Period(periodo_key, freq="M").days_in_month * 24.0
            periodo_str = str(periodo_key)

        if fila_horometro is not None:
            horas_operativas = float(fila_horometro["horas_operativas_horometro"])
            pct_utilizacion = fila_horometro["pct_utilizacion"]
            fuente_horas = "horometro_real"
        else:
            intervalos = []
            if grupo is not None:
                for _, r in grupo.iterrows():
                    ini = r.get("H_INICIO_REAL")
                    fin = r.get("H. FIN INTERV.")
                    if pd.isna(ini):
                        continue
                    if pd.isna(fin):
                        fin = ini + pd.Timedelta(hours=float(r.get("Horas_Reparacion_Neta", 0) or 0))
                    if pd.notnull(ini) and pd.notnull(fin) and fin > ini:
                        intervalos.append((ini, fin))
            horas_taller = sum(
                (f - i).total_seconds() / 3600 for i, f in _mtbs_fusionar_intervalos(intervalos)
            )
            horas_operativas = max(0.0, horas_calendario - horas_taller)
            pct_utilizacion = None
            fuente_horas = "aproximado_taller"

        mtbs_horas = round(horas_operativas / total_intervenciones, 2) if total_intervenciones > 0 else None

        filas.append({
            "codigo_equipo": equipo,
            "periodo": periodo_str,
            "horas_operativas_totales": round(horas_operativas, 2),
            "total_intervenciones": total_intervenciones,
            "mtbs_horas": mtbs_horas,
            "pct_utilizacion": round(float(pct_utilizacion), 2) if pd.notna(pct_utilizacion) else None,
            "fuente_horas": fuente_horas
        })

    resultado = pd.DataFrame(filas, columns=columnas_salida)
    if len(resultado):
        resultado = resultado.sort_values(["periodo", "codigo_equipo"]).reset_index(drop=True)
    return resultado


def construir_panel_mtbs_html(df_mtbs_mensual: pd.DataFrame, df_volvo_connect: pd.DataFrame = None) -> tuple:
    """
    Construye el fragmento HTML del panel MTBS (módulo aislado) + los JSON que
    alimentan su JS dedicado. No reutiliza ningún id/clase/función de las demás
    tarjetas del dashboard (prefijo `mtbs`/`Mtbs` exclusivo de este módulo).
    """
    def _mtbs_registros_json_seguros(df):
        # pandas convierte silenciosamente los None de columnas numéricas mixtas
        # (mtbs_horas/pct_utilizacion) a NaN al construir el DataFrame; json.dumps(nan)
        # emite el token inválido "NaN" en el <script>. Se normaliza de vuelta a None
        # (-> "null" en JSON) antes de serializar.
        registros = df.to_dict(orient="records")
        for r in registros:
            for k, v in r.items():
                if isinstance(v, float) and pd.isna(v):
                    r[k] = None
        return registros

    json_mtbs_mensual = json.dumps(_mtbs_registros_json_seguros(df_mtbs_mensual))
    json_volvo_connect = json.dumps(
        _mtbs_registros_json_seguros(df_volvo_connect) if df_volvo_connect is not None else []
    )

    html = f"""
    <div class="row mt-4">
        <div class="col-12">
            <div class="glass-panel chart-card chart-container" id="panel_mtbs_habitos">
                <div class="chart-toolbar">
                    <span class="chart-toolbar-title">
                        <i class="fa-solid fa-gauge-simple-high me-1" style="color: var(--violet);"></i>
                        Correlación MTBS vs. Hábitos Operativos — Fact_VolvoConnect
                        <span class="badge mtbs-badge-modulo ms-2">MÓDULO INDEPENDIENTE</span>
                    </span>
                    <div class="chart-toolbar-controls">
                        <select class="select-mini" id="mtbsSelectEjeXHabitos" onchange="renderMtbsCorrelacionHabitos()">
                            <option value="ralenti_pct" selected>Ralentí (%)</option>
                            <option value="pto_pct">PTO (%)</option>
                            <option value="punto_muerto_pct">En punto muerto (%)</option>
                            <option value="promedio_conduccion_kmh">Promedio de conducción (km/h)</option>
                            <option value="consumo_l_100km">Consumo (l/100 km)</option>
                        </select>
                    </div>
                </div>
                <small class="text-secondary d-block mb-2">
                    <i class="fa-solid fa-circle-info me-1"></i>
                    Cada punto es un equipo-mes real de <code>Fact_VolvoConnect</code> (telemetría Volvo Connect,
                    filtrada estrictamente a la flota Volvo FMX vía INNER JOIN contra PARQUE DE EQUIPOS — se
                    descartan automáticamente los vehículos de otras operaciones/sitios que comparten la misma
                    cuenta) cruzado con el MTBS mensual del mismo equipo/mes. Objetivo: visualizar si un ralentí
                    alto (mal hábito operativo) coincide con equipos "talleristas" (MTBS bajo, rojo).
                </small>
                <div id="chartMtbsHabitos" style="width:100%; height:400px;"></div>
            </div>
        </div>
    </div>
    """

    script = f"""
        <script>
            // ============================================================
            // MÓDULO INDEPENDIENTE — MTBS. Namespace propio (prefijo mtbs*),
            // no comparte identificadores con el resto del dashboard.
            // ============================================================
            const MTBS_MENSUAL_DATA = {json_mtbs_mensual};
            const VOLVO_CONNECT_DATA = {json_volvo_connect};

            // Umbral mínimo de horas operativas para mostrar un equipo-mes en la
            // correlación (Mejora 1): descarta picos irreales de equipos que casi no
            // trabajaron o con subregistro de paradas. Es un filtro de PRESENTACIÓN —
            // no altera MTBS_MENSUAL_DATA ni la fórmula calculada en Python.
            const MTBS_HORAS_MIN_VISIBLE = 50;
            const MTBS_TARGET_HORAS = 140;

            // Formato condicional de color por barra (Mejora 3).
            function mtbsColorPorValor(mtbs) {{
                if (mtbs < 90) return '#EF4444';
                if (mtbs < MTBS_TARGET_HORAS) return '#F59E0B';
                return '#10B981';
            }}

            // Insignia de estado en texto, para tooltips enriquecidos.
            function mtbsEstadoTexto(mtbs) {{
                if (mtbs < 90) return 'TALLERISTA';
                if (mtbs < MTBS_TARGET_HORAS) return 'ALERTA';
                return 'ÓPTIMO';
            }}

            // Regresión lineal simple (mínimos cuadrados) para la línea de tendencia
            // de los gráficos de correlación — se recalcula con cada cambio de métrica.
            function mtbsCalcularTendenciaLineal(xs, ys) {{
                const n = xs.length;
                if (n < 2) return null;
                const sumX = xs.reduce((a, b) => a + b, 0);
                const sumY = ys.reduce((a, b) => a + b, 0);
                const sumXY = xs.reduce((acc, x, i) => acc + x * ys[i], 0);
                const sumXX = xs.reduce((acc, x) => acc + x * x, 0);
                const denom = (n * sumXX - sumX * sumX);
                if (denom === 0) return null;
                const pendiente = (n * sumXY - sumX * sumY) / denom;
                const intercepto = (sumY - pendiente * sumX) / n;
                return {{ pendiente, intercepto }};
            }}

            // ============================================================
            // Correlación MTBS vs. Hábitos Operativos (Fact_VolvoConnect). Join
            // client-side por (codigo_equipo, periodo == Periodo_Volvo) contra
            // MTBS_MENSUAL_DATA — mismo criterio >50h operativas y MTBS calculable
            // ya usado en el resto del módulo, para no mezclar puntos no confiables.
            // Totalmente reactivo: cambiar la métrica del Eje X recalcula puntos,
            // escala, línea de tendencia (regresión lineal) y tooltips al instante.
            // Clic en un punto activa el filtro cruzado GLOBAL por equipo (mismo
            // `activarFiltroEquipo` que usan el resto de los gráficos del
            // dashboard); el equipo activo se resalta aquí con un anillo dorado en
            // vez de ocultar el resto de los puntos, para no perder el contexto de
            // la correlación completa.
            // ============================================================
            const MTBS_ETIQUETAS_EJE_X = {{
                ralenti_pct: 'Ralentí (%)',
                pto_pct: 'PTO (%)',
                punto_muerto_pct: 'En punto muerto (%)',
                promedio_conduccion_kmh: 'Promedio de conducción (km/h)',
                consumo_l_100km: 'Consumo (l/100 km)'
            }};

            function renderMtbsCorrelacionHabitos() {{
                const ejeXCampo = document.getElementById('mtbsSelectEjeXHabitos').value;
                const etiquetaEjeX = MTBS_ETIQUETAS_EJE_X[ejeXCampo] || ejeXCampo;

                const mtbsPorClave = {{}};
                MTBS_MENSUAL_DATA.forEach(d => {{ mtbsPorClave[d.codigo_equipo + '|' + d.periodo] = d; }});

                const puntos = [];
                VOLVO_CONNECT_DATA.forEach(v => {{
                    const m = mtbsPorClave[v.codigo_equipo + '|' + v.Periodo_Volvo];
                    if (!m || m.mtbs_horas === null || m.mtbs_horas === undefined) return;
                    if (m.horas_operativas_totales <= MTBS_HORAS_MIN_VISIBLE) return;
                    const valorX = v[ejeXCampo];
                    if (valorX === null || valorX === undefined) return;
                    puntos.push({{
                        equipo: v.codigo_equipo, periodo: v.Periodo_Volvo,
                        x: valorX, mtbs: m.mtbs_horas
                    }});
                }});

                if (!puntos.length) {{
                    Plotly.react('chartMtbsHabitos', [], {{
                        template: 'plotly_dark', paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                        annotations: [{{ text: 'Sin equipos-mes con Fact_VolvoConnect + MTBS calculable', showarrow: false, font: {{ color: '#64748b' }} }}],
                        height: 300
                    }}, {{ displaylogo: false, responsive: true }});
                    return;
                }}

                const esActivo = p => filtroEquipoActivo && p.equipo === filtroEquipoActivo;

                const trace = {{
                    type: 'scatter', mode: 'markers',
                    x: puntos.map(p => p.x),
                    y: puntos.map(p => p.mtbs),
                    customdata: puntos.map(p => [p.equipo, p.periodo, mtbsEstadoTexto(p.mtbs)]),
                    marker: {{
                        size: puntos.map(p => esActivo(p) ? 16 : 10),
                        color: puntos.map(p => mtbsColorPorValor(p.mtbs)),
                        line: {{
                            width: puntos.map(p => esActivo(p) ? 3 : 1),
                            color: puntos.map(p => esActivo(p) ? '#FFD700' : '#0d1b2e')
                        }}
                    }},
                    hovertemplate:
                        '<b>%{{customdata[0]}}</b><br>' +
                        etiquetaEjeX + ': <b>%{{x:.1f}}</b><br>' +
                        'MTBS: <b>%{{y:.1f}} h</b> · %{{customdata[2]}}<br>' +
                        'Periodo: %{{customdata[1]}}' +
                        '<extra></extra>'
                }};

                const traces = [trace];
                const tendencia = mtbsCalcularTendenciaLineal(puntos.map(p => p.x), puntos.map(p => p.mtbs));
                if (tendencia) {{
                    const xMin = Math.min(...puntos.map(p => p.x));
                    const xMax = Math.max(...puntos.map(p => p.x));
                    traces.push({{
                        type: 'scatter', mode: 'lines',
                        x: [xMin, xMax],
                        y: [tendencia.pendiente * xMin + tendencia.intercepto, tendencia.pendiente * xMax + tendencia.intercepto],
                        line: {{ color: 'rgba(167,139,250,0.65)', width: 2, dash: 'dash' }},
                        name: 'Tendencia', hoverinfo: 'skip', showlegend: false
                    }});
                }}

                const layout = {{
                    template: 'plotly_dark', paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ family: 'Inter, Segoe UI, sans-serif', color: '#e2e8f0' }},
                    hoverlabel: {{ bgcolor: 'rgba(21,28,44,0.95)', bordercolor: '#a78bfa', font: {{ family: 'JetBrains Mono, monospace', size: 12, color: '#f8fafc' }} }},
                    xaxis: {{ title: etiquetaEjeX, gridcolor: 'rgba(148,163,184,0.1)' }},
                    yaxis: {{ title: 'MTBS (h)', gridcolor: 'rgba(148,163,184,0.12)' }},
                    shapes: [{{
                        type: 'line', x0: 0, x1: 1, xref: 'paper', y0: MTBS_TARGET_HORAS, y1: MTBS_TARGET_HORAS, yref: 'y',
                        line: {{ color: '#dc2626', width: 1.5, dash: 'dot' }}
                    }}],
                    margin: {{ l: 55, r: 15, t: 15, b: 45 }},
                    height: 400,
                    transition: {{ duration: 350, easing: 'cubic-in-out' }}
                }};

                Plotly.react('chartMtbsHabitos', traces, layout, {{ displaylogo: false, responsive: true }});

                const gd = document.getElementById('chartMtbsHabitos');
                gd.removeAllListeners && gd.removeAllListeners('plotly_click');
                gd.on('plotly_click', function(evt) {{
                    if (!evt || !evt.points || !evt.points.length || !evt.points[0].customdata) return;
                    activarFiltroEquipo(evt.points[0].customdata[0]);
                }});
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                renderMtbsCorrelacionHabitos();
            }});
        </script>
    """

    return html, script


# ==============================================================================
# E. MÓDULO INDEPENDIENTE — BACKLOG (DETALLE_BKL) · FLOTA VOLVO FMX
# ==============================================================================
# Módulo aislado: solo LEE la hoja "DETALLE_BKL" y reutiliza el set de códigos
# Volvo FMX ya validado en `_mtbs_equipos_volvo_fmx` (MARCA=VOLVO, MODELO
# contiene "FMX" — único punto de verdad de ese filtro en todo el archivo, para
# no reimplementar el criterio). No modifica ni depende de ningún cálculo de
# MTBF/MTTR/Disponibilidad Mecánica/Pareto de Fallas ni del módulo MTBS —
# namespace propio `bkl`/`Bkl`/`BKL` en HTML/CSS/JS.
# ==============================================================================

_BKL_CIRCLED_NUM_RE = re.compile(r'^[①-⑳]\s*')
_BKL_DISP_LINEA_RE = re.compile(r'^([✔✓✖✗xX])\s*(\d+)\s*disp\.?', re.IGNORECASE)
_BKL_STATUS_FRACCION_RE = re.compile(r'\((\d+)\s*/\s*(\d+)\)')


def _bkl_split_lineas(valor) -> list:
    """Separa un valor de celda por saltos de línea, descartando líneas vacías
    (la hoja trae líneas en blanco intercaladas en algunos ítems, ej. fila 23)."""
    if pd.isna(valor):
        return []
    return [l.strip() for l in str(valor).split("\n") if l.strip()]


def _bkl_limpiar_codigo(codigo: str) -> str:
    """Quita el numeral circulado (①, ②...) que antecede al código en ítems NO_EJECUTADO."""
    return _BKL_CIRCLED_NUM_RE.sub("", codigo).strip()


def _bkl_parsear_linea_disponibilidad(linea: str):
    """'✔ 5 disp.' -> (True, 5); '✖ 0 disp.' -> (False, 0); si no matchea, (None, None)."""
    if not linea:
        return None, None
    m = _BKL_DISP_LINEA_RE.match(linea)
    if not m:
        return None, None
    disponible = m.group(1) in ("✔", "✓")
    return disponible, int(m.group(2))


def _bkl_parsear_status_almacen(valor):
    """
    'PARCIAL (2/3)' -> (2, 3, 66.7); 'DISPONIBLE' -> (None, None, 100.0);
    'SIN STOCK' -> (0, None, 0.0). El total/disponibles que no viene explícito en el
    texto (casos DISPONIBLE/SIN STOCK) se resuelve después con el conteo real de
    líneas de la columna CODIGO — más confiable que TOTAL_CODIGOS (ver nota abajo).
    """
    texto = str(valor).strip().lstrip("●•").strip()
    m = _BKL_STATUS_FRACCION_RE.search(texto)
    if m:
        disp, tot = int(m.group(1)), int(m.group(2))
        pct = round((disp / tot) * 100, 1) if tot > 0 else 0.0
        return disp, tot, pct, texto
    texto_up = texto.upper()
    if "SIN STOCK" in texto_up:
        return 0, None, 0.0, texto
    if "DISPONIBLE" in texto_up:
        return None, None, 100.0, texto
    return None, None, None, texto


def cargar_detalle_bkl_items(path: str, df_parque: pd.DataFrame) -> list:
    """
    Lee DETALLE_BKL a nivel de ÍTEM (una fila del Excel = un backlog = una tarjeta),
    separando por saltos de línea las columnas multi-repuesto (CODIGO, CANTIDAD,
    DESCRIPCION, CODIGOS_DISPONIBLES) y extrayendo (disponibles, total, %) de
    STATUS_ALMACEN. Módulo aislado — reutiliza `_mtbs_equipos_volvo_fmx` como único
    criterio de filtro de flota, igual que `cargar_detalle_backlog`, pero NO comparte
    ni modifica esa función: alimenta una vista distinta ("Gestión de Backlog" en
    tarjetas), independiente del panel agregado de barras por semana/equipo.

    NOTA DE CALIDAD DE DATO: en los ítems NO_EJECUTADO, la columna TOTAL_CODIGOS trae
    texto tipo "REP 1 (66)\\nREP 2 (32)" en vez de un conteo numérico (parece un bug de
    la Macro de origen para esos registros). Por eso el total de repuestos por ítem NO
    se lee de TOTAL_CODIGOS: se deriva de la fracción en STATUS_ALMACEN (fuente más
    confiable, ej. "PARCIAL (2/3)") y, en su defecto, del conteo de líneas de CODIGO.
    """
    try:
        df = pd.read_excel(path, sheet_name=SHEET_DETALLE_BKL)
    except Exception as e:
        print(f"⚠️  Aviso (Gestión de Backlog): no se pudo leer la hoja '{SHEET_DETALLE_BKL}': {e}")
        return []

    df.columns = [str(c).strip() for c in df.columns]

    columnas_requeridas = ["N_ITEM", "CODIGO_EQUIPO", "FECHA_BACKLOG", "ESTADO"]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        print(f"⚠️  Aviso (Gestión de Backlog): faltan columnas obligatorias {faltantes}. Se omite la vista.")
        return []

    df = df.dropna(subset=["CODIGO_EQUIPO", "FECHA_BACKLOG"]).copy()
    df["CODIGO_EQUIPO"] = df["CODIGO_EQUIPO"].astype(str).str.strip().str.upper()

    equipos_fmx = _mtbs_equipos_volvo_fmx(df_parque)
    df = df[df["CODIGO_EQUIPO"].isin(equipos_fmx)].copy()

    df["FECHA_BACKLOG"] = pd.to_datetime(df["FECHA_BACKLOG"], errors="coerce")
    df = df.dropna(subset=["FECHA_BACKLOG"]).copy()
    df["FECHA_CIERRE"] = pd.to_datetime(df["FECHA_CIERRE"], errors="coerce") if "FECHA_CIERRE" in df.columns else pd.NaT

    # Cruce con el catálogo general de equipos (PARQUE DE EQUIPOS) para asignar la
    # categoría de flota a cada ítem — mismo criterio que el resto del dashboard
    # (`clasificar_categoria_flota`, columna "Contrato_Gold"), para que el filtro de
    # Flota del panel de tarjetas sea consistente con la tabla principal de KPIs.
    contrato_gold_dict = dict(zip(df_parque["COD INTERNO"], df_parque["Contrato_Gold"]))

    items = []
    for idx, r in df.iterrows():
        codigos = [_bkl_limpiar_codigo(c) for c in _bkl_split_lineas(r.get("CODIGO"))]
        cantidades = _bkl_split_lineas(r.get("CANTIDAD"))
        descripciones = _bkl_split_lineas(r.get("DESCRIPCION"))
        disponibilidad_lineas = _bkl_split_lineas(r.get("CODIGOS_DISPONIBLES"))
        # Caso EJECUTADO: CODIGOS_DISPONIBLES suele ser un número escalar único (sin
        # desglose por repuesto), no una lista de líneas "✔ N disp." — se detecta un
        # único valor no parseable como línea de disponibilidad.
        disponibilidad_escalar = None
        if len(disponibilidad_lineas) <= 1:
            bruto = r.get("CODIGOS_DISPONIBLES")
            if pd.notnull(bruto) and str(bruto).strip().replace(".", "", 1).isdigit():
                disponibilidad_escalar = int(float(bruto))

        detalle = []
        for i, codigo in enumerate(codigos):
            cantidad_val = cantidades[i] if i < len(cantidades) else None
            cantidad_num = int(float(cantidad_val)) if cantidad_val and cantidad_val.replace(".", "", 1).isdigit() else cantidad_val
            descripcion_val = descripciones[i] if i < len(descripciones) else ""
            linea_disp = disponibilidad_lineas[i] if i < len(disponibilidad_lineas) else None
            disponible, cant_disp = _bkl_parsear_linea_disponibilidad(linea_disp) if linea_disp else (None, None)
            detalle.append({
                "codigo": codigo,
                "cantidad": cantidad_num,
                "descripcion": descripcion_val,
                "disponible": disponible,
                "cantidad_disponible": cant_disp,
            })

        disp_status, tot_status, pct_status, status_texto = _bkl_parsear_status_almacen(r.get("STATUS_ALMACEN"))
        total_real = tot_status if tot_status is not None else (len(codigos) if codigos else 0)

        if disp_status is not None:
            disp_real = disp_status
        elif pct_status == 100.0:
            disp_real = total_real
        elif disponibilidad_escalar is not None:
            disp_real = disponibilidad_escalar
        elif detalle:
            disp_real = sum(1 for d in detalle if d["disponible"] is True)
        else:
            disp_real = 0

        pct_real = round((disp_real / total_real) * 100, 1) if total_real else 0.0
        fecha_cierre_val = r.get("FECHA_CIERRE")

        contrato_gold_val = str(contrato_gold_dict.get(r["CODIGO_EQUIPO"], "NO ESPECIFICADO"))
        categoria_val = clasificar_categoria_flota(r["CODIGO_EQUIPO"], contrato_gold_val)

        items.append({
            "uid": idx,
            "n_item": int(r["N_ITEM"]) if pd.notnull(r["N_ITEM"]) else idx,
            "codigo_equipo": r["CODIGO_EQUIPO"],
            "categoria": categoria_val,
            "chasis": str(r.get("CHASIS", "")).strip() if pd.notnull(r.get("CHASIS")) else "",
            "fecha_backlog": r["FECHA_BACKLOG"].strftime("%Y-%m-%d"),
            "estado": str(r.get("ESTADO", "")).strip().upper(),
            "observacion": str(r.get("OBSERVACION", "")).strip() if pd.notnull(r.get("OBSERVACION")) else "",
            "solicitante": str(r.get("SOLICITANTE", "")).strip() if pd.notnull(r.get("SOLICITANTE")) else "",
            "fecha_cierre": fecha_cierre_val.strftime("%Y-%m-%d") if pd.notnull(fecha_cierre_val) else None,
            "total_repuestos": total_real,
            "disponibles_almacen": disp_real,
            "pct_almacen": pct_real,
            "status_almacen_texto": status_texto,
            "detalle": detalle,
        })

    print(f"🗃️  Gestión de Backlog (vista tarjetas) — {len(items)} ítems Volvo FMX cargados desde '{SHEET_DETALLE_BKL}'.")
    return items


def construir_panel_bkl_cards_html(items_bkl: list) -> tuple:
    """
    Panel "Gestión de Backlog" — vista en tarjetas (una por ítem/N_ITEM), con barra
    de disponibilidad de repuestos y detalle desplegable (Código/Cantidad/Descripción/
    Disponibilidad). Módulo aislado, prefijo `bklCards`/`BKL_ITEMS` exclusivo. Único
    panel de Backlog del dashboard: incluye los 2 KPI resumen (% Cumplimiento,
    Pendientes) además de los indicadores de disponibilidad de repuestos — ya no hay
    un panel de barras por semana separado.
    """
    json_bkl_items = json.dumps(items_bkl)

    equipos_disponibles = sorted({it["codigo_equipo"] for it in items_bkl})
    opciones_equipo_html = "\n".join(f'<option value="{eq}">{eq}</option>' for eq in equipos_disponibles)

    html = f"""
    <div class="row mt-2">
        <div class="col-12">
            <style>
                .bkl-cards-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
                    gap: 14px;
                }}
                .bkl-card {{
                    background: rgba(17, 24, 39, 0.55);
                    border: 1px solid rgba(148,163,184,0.14);
                    border-radius: 14px;
                    overflow: hidden;
                    transition: border-color 0.2s ease, transform 0.15s ease;
                }}
                .bkl-card:hover {{ border-color: rgba(56,189,248,0.35); transform: translateY(-2px); }}
                .bkl-card-header {{ padding: 14px 16px 10px; cursor: pointer; display: flex; flex-direction: column; gap: 6px; }}
                .bkl-card-top-row {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }}
                .bkl-card-equipo {{ font-weight: 800; font-size: 1.05rem; color: #f8fafc; letter-spacing:0.02em; }}
                .bkl-card-fecha {{ font-size: 0.72rem; color: var(--muted); }}
                .bkl-badge-estado {{ font-size: 0.65rem; font-weight: 700; padding: 3px 9px; border-radius: 20px; letter-spacing:0.04em; white-space: nowrap; }}
                .bkl-badge-no-ejecutado {{ background: rgba(220,38,38,0.15); color: #f87171; border: 1px solid var(--critical); }}
                .bkl-badge-ejecutado {{ background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid var(--ok); }}
                .bkl-progress-track {{ height: 8px; border-radius: 6px; background: rgba(148,163,184,0.15); overflow: hidden; margin-top: 4px; }}
                .bkl-progress-fill {{ height: 100%; border-radius: 6px; transition: width 0.4s ease; }}
                .bkl-progress-label {{ display:flex; justify-content:space-between; font-size:0.68rem; color: var(--muted); margin-top:3px; }}
                .bkl-card-desc {{ font-size: 0.78rem; color: #cbd5e1; margin-top: 4px; line-height:1.3; }}
                .bkl-card-toggle {{ font-size: 0.7rem; color: var(--cyan); display:flex; align-items:center; gap:4px; margin-top:6px; }}
                .bkl-card-toggle i {{ transition: transform 0.2s ease; }}
                .bkl-card.expanded .bkl-card-toggle i {{ transform: rotate(180deg); }}
                .bkl-card-body {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease; border-top: 1px solid rgba(148,163,184,0.1); }}
                .bkl-card.expanded .bkl-card-body {{ max-height: 700px; }}
                .bkl-detalle-table {{ width:100%; border-collapse: collapse; font-size: 0.76rem; }}
                .bkl-detalle-table th {{ text-align:left; color: var(--muted); font-weight:600; padding: 6px 10px; border-bottom:1px solid rgba(148,163,184,0.12); }}
                .bkl-detalle-table td {{ padding: 6px 10px; border-bottom:1px solid rgba(148,163,184,0.06); color:#e2e8f0; }}
                .bkl-disp-si {{ color:#34d399; }}
                .bkl-disp-no {{ color:#f87171; }}
                .bkl-card-meta {{ padding: 8px 16px 12px; font-size:0.72rem; color: var(--muted); display:flex; flex-wrap:wrap; gap: 4px 14px; }}
            </style>

            <div class="glass-panel chart-card chart-container" id="panel_bkl_cards">
                <div class="chart-toolbar">
                    <span class="chart-toolbar-title">
                        <i class="fa-solid fa-boxes-stacked me-1" style="color: var(--orange);"></i>
                        Gestión de Backlog — Repuestos por Ítem
                        <span class="badge bkl-badge-modulo ms-2">MÓDULO INDEPENDIENTE</span>
                    </span>
                    <div class="chart-toolbar-controls">
                        <input type="text" class="input-kpi" id="bklCardsBuscador" placeholder="Buscar equipo, código o descripción..." oninput="renderBklCards()">
                        <select class="select-mini" id="bklCardsSelectEstado" onchange="renderBklCards()">
                            <option value="ALL">Todos los estados</option>
                            <option value="NO_EJECUTADO" selected>No ejecutado</option>
                            <option value="EJECUTADO">Ejecutado</option>
                        </select>
                        <select class="select-mini" id="bklCardsSelectEquipo" onchange="renderBklCards()">
                            <option value="ALL" selected>Flota completa</option>
                            {opciones_equipo_html}
                        </select>
                        <select class="select-mini" id="bklCardsSelectFlota" onchange="renderBklCards()">
                            <option value="ALL" selected>Todos</option>
                            <option value="CONTRATO">Contrato</option>
                            <option value="CLIENTE">Cliente</option>
                        </select>
                        <select class="select-mini" id="bklCardsSelectDisponibilidad" onchange="renderBklCards()">
                            <option value="ALL" selected>Cualquier disponibilidad</option>
                            <option value="COMPLETO">Completo (100%)</option>
                            <option value="PARCIAL">Parcial</option>
                            <option value="SIN_STOCK">Sin stock (0%)</option>
                        </select>
                        <button class="btn-fullscreen" onclick="toggleFullscreen('panel_bkl_cards')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                    </div>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md-2 col-4">
                        <div class="kpi-card" style="padding:12px 16px;">
                            <i class="fa-solid fa-circle-check kpi-icon" style="color: var(--ok);"></i>
                            <div class="kpi-title">% Cumplimiento Backlog</div>
                            <div class="kpi-value" style="font-size:1.8rem; color: var(--ok);" id="bklCardsKpiCumplimiento">0%</div>
                        </div>
                    </div>
                    <div class="col-md-2 col-4">
                        <div class="kpi-card" style="padding:12px 16px;">
                            <i class="fa-solid fa-triangle-exclamation kpi-icon" style="color: var(--critical);"></i>
                            <div class="kpi-title">Total Pendientes</div>
                            <div class="kpi-value" style="font-size:1.8rem; color: var(--critical);" id="bklCardsKpiPendientes">0</div>
                        </div>
                    </div>
                    <div class="col-md-2 col-4">
                        <div class="kpi-card" style="padding:12px 16px;">
                            <i class="fa-solid fa-boxes-stacked kpi-icon" style="color: var(--cyan);"></i>
                            <div class="kpi-title">Ítems Mostrados</div>
                            <div class="kpi-value" style="font-size:1.8rem; color: var(--cyan);" id="bklCardsKpiTotal">0</div>
                        </div>
                    </div>
                    <div class="col-md-2 col-4">
                        <div class="kpi-card" style="padding:12px 16px;">
                            <i class="fa-solid fa-circle-check kpi-icon" style="color: var(--ok);"></i>
                            <div class="kpi-title">Repuestos Completos</div>
                            <div class="kpi-value" style="font-size:1.8rem; color: var(--ok);" id="bklCardsKpiCompletos">0</div>
                        </div>
                    </div>
                    <div class="col-md-2 col-4">
                        <div class="kpi-card" style="padding:12px 16px;">
                            <i class="fa-solid fa-triangle-exclamation kpi-icon" style="color: var(--warning);"></i>
                            <div class="kpi-title">Parciales</div>
                            <div class="kpi-value" style="font-size:1.8rem; color: var(--warning);" id="bklCardsKpiParciales">0</div>
                        </div>
                    </div>
                    <div class="col-md-2 col-4">
                        <div class="kpi-card" style="padding:12px 16px;">
                            <i class="fa-solid fa-circle-xmark kpi-icon" style="color: var(--critical);"></i>
                            <div class="kpi-title">Sin Stock</div>
                            <div class="kpi-value" style="font-size:1.8rem; color: var(--critical);" id="bklCardsKpiSinStock">0</div>
                        </div>
                    </div>
                </div>

                <div id="bklCardsContenedor" class="bkl-cards-grid"></div>
                <div id="bklCardsSinResultados" class="text-center text-secondary py-4" style="display:none;">
                    Sin ítems de backlog para este filtro.
                </div>
            </div>
        </div>
    </div>
    """

    script = f"""
        <script>
            const BKL_ITEMS = {json_bkl_items};

            function renderBklCards() {{
                const buscador = (document.getElementById('bklCardsBuscador').value || '').trim().toUpperCase();
                const estadoSel = document.getElementById('bklCardsSelectEstado').value;
                const equipoSel = document.getElementById('bklCardsSelectEquipo').value;
                const flotaSel = document.getElementById('bklCardsSelectFlota').value;
                const dispSel = document.getElementById('bklCardsSelectDisponibilidad').value;

                let items = BKL_ITEMS.filter(it => {{
                    if (estadoSel !== 'ALL' && it.estado !== estadoSel) return false;
                    if (equipoSel !== 'ALL' && it.codigo_equipo !== equipoSel) return false;
                    if (flotaSel !== 'ALL' && it.categoria !== flotaSel) return false;
                    if (dispSel === 'COMPLETO' && it.pct_almacen < 100) return false;
                    if (dispSel === 'SIN_STOCK' && it.pct_almacen > 0) return false;
                    if (dispSel === 'PARCIAL' && (it.pct_almacen <= 0 || it.pct_almacen >= 100)) return false;
                    if (buscador) {{
                        const haystack = (it.codigo_equipo + ' ' + it.observacion + ' ' +
                            it.detalle.map(d => d.codigo + ' ' + d.descripcion).join(' ')).toUpperCase();
                        if (!haystack.includes(buscador)) return false;
                    }}
                    return true;
                }});

                const cont = document.getElementById('bklCardsContenedor');
                const sinResultados = document.getElementById('bklCardsSinResultados');

                const ejecutados = items.filter(it => it.estado === 'EJECUTADO').length;
                const pendientes = items.length - ejecutados;
                const pctCumplimiento = items.length > 0 ? Math.round((ejecutados / items.length) * 1000) / 10 : 0;

                document.getElementById('bklCardsKpiCumplimiento').textContent = pctCumplimiento.toFixed(1) + '%';
                document.getElementById('bklCardsKpiPendientes').textContent = pendientes;
                document.getElementById('bklCardsKpiTotal').textContent = items.length;
                document.getElementById('bklCardsKpiCompletos').textContent = items.filter(it => it.pct_almacen >= 100).length;
                document.getElementById('bklCardsKpiParciales').textContent = items.filter(it => it.pct_almacen > 0 && it.pct_almacen < 100).length;
                document.getElementById('bklCardsKpiSinStock').textContent = items.filter(it => it.pct_almacen <= 0).length;

                if (!items.length) {{
                    cont.innerHTML = '';
                    sinResultados.style.display = '';
                    return;
                }}
                sinResultados.style.display = 'none';

                items = [...items].sort((a, b) => new Date(b.fecha_backlog) - new Date(a.fecha_backlog));

                cont.innerHTML = items.map(it => {{
                    const pct = Math.max(0, Math.min(100, it.pct_almacen));
                    const color = pct >= 100 ? 'var(--ok)' : (pct <= 0 ? 'var(--critical)' : 'var(--warning)');
                    const badgeClass = it.estado === 'NO_EJECUTADO' ? 'bkl-badge-no-ejecutado' : 'bkl-badge-ejecutado';
                    const badgeTexto = it.estado === 'NO_EJECUTADO' ? 'NO EJECUTADO' : 'EJECUTADO';
                    const cardId = 'bklCard_' + it.uid;

                    const filasDetalle = it.detalle.map(d => {{
                        let dispTxt, dispClase;
                        if (d.disponible === true) {{ dispTxt = '✔ ' + (d.cantidad_disponible != null ? d.cantidad_disponible : '') + ' disp.'; dispClase = 'bkl-disp-si'; }}
                        else if (d.disponible === false) {{ dispTxt = '✖ ' + (d.cantidad_disponible != null ? d.cantidad_disponible : 0) + ' disp.'; dispClase = 'bkl-disp-no'; }}
                        else {{ dispTxt = '—'; dispClase = ''; }}
                        return `<tr>
                            <td>${{d.codigo || '—'}}</td>
                            <td>${{d.cantidad != null ? d.cantidad : '—'}}</td>
                            <td>${{d.descripcion || '—'}}</td>
                            <td class="${{dispClase}}">${{dispTxt}}</td>
                        </tr>`;
                    }}).join('');

                    const descPrincipal = (it.detalle[0] && it.detalle[0].descripcion) || it.observacion || 'Sin descripción';
                    const descExtra = it.detalle.length > 1 ? ' <span class="text-secondary">+' + (it.detalle.length - 1) + ' repuesto(s) más</span>' : '';

                    return `<div class="bkl-card" id="${{cardId}}">
                        <div class="bkl-card-header" onclick="toggleBklCard('${{cardId}}')">
                            <div class="bkl-card-top-row">
                                <div>
                                    <div class="bkl-card-equipo">${{it.codigo_equipo}}</div>
                                    <div class="bkl-card-fecha"><i class="fa-regular fa-calendar me-1"></i>${{it.fecha_backlog}} · Ítem #${{it.n_item}}</div>
                                </div>
                                <span class="bkl-badge-estado ${{badgeClass}}">${{badgeTexto}}</span>
                            </div>
                            <div class="bkl-card-desc">${{descPrincipal}}${{descExtra}}</div>
                            <div class="bkl-progress-track"><div class="bkl-progress-fill" style="width:${{pct}}%; background:${{color}};"></div></div>
                            <div class="bkl-progress-label">
                                <span>Repuestos en almacén</span>
                                <span style="color:${{color}}; font-weight:700;">${{it.disponibles_almacen}}/${{it.total_repuestos}} (${{pct.toFixed(0)}}%)</span>
                            </div>
                            <div class="bkl-card-toggle"><i class="fa-solid fa-chevron-down"></i> Ver detalle de repuestos</div>
                        </div>
                        <div class="bkl-card-body">
                            <table class="bkl-detalle-table">
                                <thead><tr><th>Código</th><th>Cant.</th><th>Descripción</th><th>Disponibilidad</th></tr></thead>
                                <tbody>${{filasDetalle || '<tr><td colspan="4" class="text-secondary">Sin repuestos detallados</td></tr>'}}</tbody>
                            </table>
                            <div class="bkl-card-meta">
                                ${{it.solicitante ? '<span><i class="fa-regular fa-user me-1"></i>' + it.solicitante + '</span>' : ''}}
                                ${{it.fecha_cierre ? '<span><i class="fa-solid fa-flag-checkered me-1"></i>Cerrado: ' + it.fecha_cierre + '</span>' : ''}}
                                ${{it.chasis ? '<span><i class="fa-solid fa-truck me-1"></i>Chasis ' + it.chasis + '</span>' : ''}}
                            </div>
                        </div>
                    </div>`;
                }}).join('');
            }}

            function toggleBklCard(cardId) {{
                const card = document.getElementById(cardId);
                if (card) card.classList.toggle('expanded');
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                renderBklCards();
            }});
        </script>
    """

    return html, script


# ==============================================================================
# F. MÓDULO INDEPENDIENTE — ESTADO DE FLOTA DEL DÍA (junto al Velocímetro DM)
# ==============================================================================
# Tarjeta ubicada al costado derecho del Velocímetro DM Global (misma fila),
# con selector de fecha propio. Lee "Registro de Intervenciones" completo —
# SIN el filtro "APLICA KPI" que sí usa `preparar_raw_intervenciones_js` para
# el cálculo de DM global, porque aquí interesa CUALQUIER intervención del día
# registrada, aplique o no al cálculo de Disponibilidad Mecánica — y expone el
# resumen operativo/en proceso/inoperativo de la fecha seleccionada. Namespace
# aislado `efd`/`EFD_*` en HTML/CSS/JS: no comparte identificadores con el
# resto del dashboard (sí reutiliza helpers globales ya usados por MTBS/
# Backlog: `activarFiltroEquipo`, `toggleFullscreen`).
# ==============================================================================

def _valor_descripcion_intervencion_dia(fila) -> str:
    """
    "Detalle del trabajo" para el panel Estado de Flota del Día. El
    requerimiento original pide la "columna J / DESCRIPCION", pero en el Excel
    real de "Registro de Intervenciones" la columna J es "INGRESO POR" (quién
    generó el registro, no el detalle del trabajo realizado) — no existe una
    columna literal "DESCRIPCION". El campo semánticamente equivalente ("qué
    se hizo/encontró") es "TRABAJO REALIZADO" (columna M); si viene vacío
    (intervención recién abierta, aún sin cierre) se cae a "SÍNTOMA" (columna
    K), luego "CAUSA" (columna L) y, en último caso, a "INGRESO POR"
    (columna J), para que la celda nunca quede en blanco.
    """
    for col in ("TRABAJO REALIZADO", "SÍNTOMA", "CAUSA", "INGRESO POR"):
        valor = fila.get(col)
        if pd.notna(valor) and str(valor).strip():
            return str(valor).strip()
    return ""


def preparar_registros_flota_dia_js(df_intervenciones: pd.DataFrame) -> list:
    """
    Registros crudos (uno por fila de "Registro de Intervenciones", ambos
    turnos del día incluidos — cada fila ya trae su propia franja horaria de
    inicio/fin, no hay columna TURNO explícita que distinguir) para el panel
    Estado de Flota del Día. Mapeo de columnas verificado contra el Excel real:
    B=FECHA, H=H. INICIO INTERV., I=H. FIN INTERV., P=CONDICIÓN (OPERATIVO/
    INOPERATIVO). El filtro por fecha y el resumen operativo/en proceso/
    inoperativo se recalculan 100% en JS (`renderEfdPanel`) al cambiar el
    selector de fecha, sin recargar la página.
    """
    datos = []
    for _, fila in df_intervenciones.iterrows():
        fecha = fila.get("FECHA")
        if pd.isna(fecha):
            continue
        inicio = fila.get("H. INICIO INTERV.")
        fin = fila.get("H. FIN INTERV.")
        estado_val = fila.get("CONDICIÓN")

        datos.append({
            "equipo": str(fila.get("EQUIPO", "")).strip(),
            "fecha": fecha.strftime("%Y-%m-%d"),
            "inicio": inicio.strftime("%Y-%m-%dT%H:%M:%S") if pd.notnull(inicio) else "",
            "fin": fin.strftime("%Y-%m-%dT%H:%M:%S") if pd.notnull(fin) else "",
            "descripcion": _valor_descripcion_intervencion_dia(fila),
            # Ya viene "OPERATIVO"/"INOPERATIVO" (mayúsculas, sin espacios) o NaN
            # porque `cargar_intervenciones` limpia la columna "CONDICIÓN" al cargar.
            "estado": "" if pd.isna(estado_val) else str(estado_val),
        })
    return datos


def construir_panel_estado_flota_dia_html(df_intervenciones: pd.DataFrame, total_flota: int = TOTAL_FLOTA_EQUIPOS) -> tuple:
    """
    Construye el fragmento HTML de la tarjeta "Estado de Flota del Día" (para
    insertar junto al Velocímetro DM, misma fila) + su <script> dedicado.
    Devuelve (html, script) — mismo patrón que `construir_panel_mtbs_html`/
    `construir_panel_bkl_cards_html`.
    """
    json_registros = json.dumps(preparar_registros_flota_dia_js(df_intervenciones))

    fecha_max = df_intervenciones["FECHA"].max()
    fecha_default = fecha_max.strftime("%Y-%m-%d") if pd.notnull(fecha_max) else ""

    html = f"""
        <style>
            .efd-badge-modulo {{
                background: rgba(34,211,238,0.14); color: var(--cyan); border: 1px solid rgba(34,211,238,0.5);
                font-size: 0.62rem; font-weight: 700; letter-spacing: 0.04em; vertical-align: middle;
            }}
            .efd-summary-banner {{
                font-family: 'JetBrains Mono', monospace; font-size: 0.84rem; line-height: 1.55; color: #e2e8f0;
                background: rgba(9,13,22,0.55); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;
                padding: 10px 14px; margin: 4px 0 14px;
            }}
            .efd-summary-banner b {{ color: var(--blue); font-weight: 800; }}
            .efd-kpi-row {{ display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }}
            .efd-kpi-chip {{
                flex: 1 1 0; min-width: 88px; text-align: center; border-radius: 12px; padding: 10px 8px;
                border: 1px solid rgba(255,255,255,0.08); background: rgba(17,24,39,0.5);
            }}
            .efd-kpi-chip-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 800; line-height: 1; }}
            .efd-kpi-chip-label {{ font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; margin-top: 4px; font-weight: 700; }}
            .efd-chip-ok {{ border-color: rgba(16,185,129,0.4); }}
            .efd-chip-ok .efd-kpi-chip-value {{ color: #34d399; }}
            .efd-chip-proceso {{ border-color: rgba(245,158,11,0.4); }}
            .efd-chip-proceso .efd-kpi-chip-value {{ color: #fbbf24; }}
            .efd-chip-inop {{ border-color: rgba(220,38,38,0.4); }}
            .efd-chip-inop .efd-kpi-chip-value {{ color: #f87171; }}
            .efd-badge-operativo {{
                background-color: rgba(16,185,129,0.15); color: #34d399; border: 1px solid var(--ok);
                font-weight: 700; font-size: 0.66rem; padding: 3px 9px; border-radius: 20px; letter-spacing: 0.03em; white-space: nowrap;
            }}
            .efd-badge-inoperativo {{
                background-color: rgba(220,38,38,0.15); color: #f87171; border: 1px solid var(--critical);
                font-weight: 700; font-size: 0.66rem; padding: 3px 9px; border-radius: 20px; letter-spacing: 0.03em; white-space: nowrap;
                box-shadow: 0 0 10px rgba(220,38,38,0.3);
            }}
            .efd-badge-proceso {{
                background: rgba(245,158,11,0.18); color: #fbbf24; border: 1px solid var(--warning);
                font-weight: 700; font-size: 0.66rem; padding: 3px 9px; border-radius: 20px; letter-spacing: 0.03em; white-space: nowrap;
                animation: efdPulseAmber 1.3s ease-in-out infinite;
            }}
            @keyframes efdPulseAmber {{
                0%, 100% {{ box-shadow: 0 0 6px rgba(245,158,11,0.4); }}
                50% {{ box-shadow: 0 0 16px rgba(245,158,11,0.9); }}
            }}
            .efd-badge-nd {{
                background: rgba(148,163,184,0.14); color: #94a3b8; border: 1px solid rgba(148,163,184,0.4);
                font-weight: 700; font-size: 0.66rem; padding: 3px 9px; border-radius: 20px; white-space: nowrap;
            }}
            .efd-table-wrapper table.table-custom {{ min-width: unset; }}
            .efd-table-wrapper th, .efd-table-wrapper td {{ padding: 8px 10px; font-size: 0.76rem; }}
            .efd-desc-cell {{ max-width: 240px; white-space: normal; color: #cbd5e1; }}
        </style>

        <div class="glass-panel chart-card chart-container h-100" id="panel_efd">
            <div class="chart-toolbar">
                <span class="chart-toolbar-title">
                    <i class="fa-solid fa-calendar-day me-1" style="color: var(--cyan);"></i>
                    Estado de Flota del Día
                    <span class="badge efd-badge-modulo ms-2">MÓDULO INDEPENDIENTE</span>
                </span>
                <div class="chart-toolbar-controls">
                    <input type="date" id="efdFechaSelector" class="input-kpi" value="{fecha_default}" onchange="renderEfdPanel()" title="Filtra las intervenciones de ambos turnos de este día">
                    <button class="btn-fullscreen" onclick="toggleFullscreen('panel_efd')" title="Pantalla completa"><i class="fa-solid fa-expand"></i></button>
                </div>
            </div>

            <div class="efd-summary-banner" id="efdResumenBanner">Cargando resumen del día...</div>

            <div class="efd-kpi-row">
                <div class="efd-kpi-chip efd-chip-ok">
                    <div class="efd-kpi-chip-value" id="efdCountOperativos">—</div>
                    <div class="efd-kpi-chip-label">Operativos</div>
                </div>
                <div class="efd-kpi-chip efd-chip-proceso">
                    <div class="efd-kpi-chip-value" id="efdCountProceso">—</div>
                    <div class="efd-kpi-chip-label">En Proceso</div>
                </div>
                <div class="efd-kpi-chip efd-chip-inop">
                    <div class="efd-kpi-chip-value" id="efdCountInoperativos">—</div>
                    <div class="efd-kpi-chip-label">Inoperativos</div>
                </div>
            </div>

            <div class="table-wrapper efd-table-wrapper" style="max-height:220px;">
                <table class="table table-custom table-hover mb-0">
                    <thead>
                        <tr>
                            <th>EQUIPO</th>
                            <th>H. INICIO</th>
                            <th>H. FIN</th>
                            <th>DESCRIPCIÓN</th>
                            <th>ESTADO</th>
                        </tr>
                    </thead>
                    <tbody id="efdTablaBody"></tbody>
                </table>
            </div>
            <small class="text-secondary mt-2" id="efdSinDatos" style="display:none;">
                <i class="fa-solid fa-circle-info me-1"></i>Sin intervenciones registradas en "Registro de Intervenciones" para la fecha seleccionada.
            </small>
        </div>
    """

    script = f"""
        <script>
            // ============================================================
            // MÓDULO INDEPENDIENTE — Estado de Flota del Día. Namespace propio
            // (prefijo efd*/EFD_*), no comparte identificadores con el resto del
            // dashboard.
            // ============================================================
            const EFD_TOTAL_FLOTA = {total_flota};
            const EFD_REGISTROS = {json_registros};

            function efdFormatoHora(iso) {{
                if (!iso) return '—';
                const d = new Date(iso);
                if (isNaN(d.getTime())) return '—';
                return d.toLocaleTimeString('es-PE', {{ hour: '2-digit', minute: '2-digit', hour12: false }});
            }}

            function efdBadgeHtml(estado) {{
                if (estado === 'EN PROCESO') {{
                    return '<span class="efd-badge-proceso"><i class="fa-solid fa-clock-rotate-left me-1"></i>EN PROCESO</span>';
                }}
                if (estado === 'INOPERATIVO') {{
                    return '<span class="efd-badge-inoperativo"><i class="fa-solid fa-triangle-exclamation me-1"></i>INOPERATIVO</span>';
                }}
                if (estado === 'OPERATIVO') {{
                    return '<span class="efd-badge-operativo"><i class="fa-solid fa-check me-1"></i>OPERATIVO</span>';
                }}
                return '<span class="efd-badge-nd">S/D</span>';
            }}

            // Regla de negocio del panel (criterio del usuario — NO se infiere nada):
            // el estado de cada equipo lo decide, literalmente, el texto que la
            // supervisión escribe en la columna P/CONDICIÓN ese día: "OPERATIVO",
            // "INOPERATIVO" o "EN PROCESO". No se deriva "en proceso" a partir de si
            // la columna I (Hora Fin) está vacía — un equipo INOPERATIVO sin Hora Fin
            // sigue contando como INOPERATIVO salvo que la propia columna P diga
            // literalmente "EN PROCESO". Si un equipo tiene ambas filas ese día
            // (p.ej. cerró un INOPERATIVO en el turno día y abrió otro marcado EN
            // PROCESO en el turno noche), EN PROCESO tiene prioridad por ser el
            // estado vigente más reciente. El resto de la flota (Total Flota - En
            // Proceso - Inoperativos) se reporta operativa.
            function efdCalcularResumen(registrosDia) {{
                const estadoPorEquipo = {{}};
                registrosDia.forEach(r => {{
                    if (r.estado === 'EN PROCESO') {{
                        estadoPorEquipo[r.equipo] = 'PROCESO';
                    }} else if (r.estado === 'INOPERATIVO' && estadoPorEquipo[r.equipo] !== 'PROCESO') {{
                        estadoPorEquipo[r.equipo] = 'INOPERATIVO';
                    }}
                }});
                const estados = Object.values(estadoPorEquipo);
                const nProceso = estados.filter(v => v === 'PROCESO').length;
                const nInoperativos = estados.filter(v => v === 'INOPERATIVO').length;
                const nOperativos = Math.max(0, EFD_TOTAL_FLOTA - nProceso - nInoperativos);
                return {{ nProceso, nInoperativos, nOperativos }};
            }}

            function renderEfdPanel() {{
                const fechaSel = document.getElementById('efdFechaSelector').value;
                const tbody = document.getElementById('efdTablaBody');
                const sinDatos = document.getElementById('efdSinDatos');

                const registrosDia = fechaSel ? EFD_REGISTROS.filter(r => r.fecha === fechaSel) : [];
                const {{ nProceso, nInoperativos, nOperativos }} = efdCalcularResumen(registrosDia);

                document.getElementById('efdCountOperativos').innerText = nOperativos;
                document.getElementById('efdCountProceso').innerText = nProceso;
                document.getElementById('efdCountInoperativos').innerText = nInoperativos;
                document.getElementById('efdResumenBanner').innerHTML =
                    'De ' + EFD_TOTAL_FLOTA + ' equipos se tiene <b>' + nProceso + '</b> en proceso en la fecha actual, ' +
                    '<b>' + nInoperativos + '</b> inoperativos, dándonos un cálculo de <b>' + nOperativos + '</b> equipos operativos.';

                tbody.innerHTML = '';
                sinDatos.style.display = registrosDia.length ? 'none' : 'block';

                const prioridadEstado = e => (e === 'INOPERATIVO' ? 0 : (e === 'EN PROCESO' ? 1 : (e === 'OPERATIVO' ? 3 : 2)));
                const filasOrdenadas = [...registrosDia].sort((a, b) => {{
                    const pa = prioridadEstado(a.estado), pb = prioridadEstado(b.estado);
                    if (pa !== pb) return pa - pb;
                    return (a.inicio || '').localeCompare(b.inicio || '');
                }});

                filasOrdenadas.forEach(r => {{
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><span class="badge-equipo" style="cursor:pointer;" onclick="activarFiltroEquipo('${{r.equipo}}')" title="Filtrar todo el dashboard por este equipo">${{r.equipo}}</span></td>
                        <td>${{efdFormatoHora(r.inicio)}}</td>
                        <td>${{efdFormatoHora(r.fin)}}</td>
                        <td class="efd-desc-cell">${{r.descripcion || '—'}}</td>
                        <td>${{efdBadgeHtml(r.estado)}}</td>
                    `;
                    tbody.appendChild(tr);
                }});
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                renderEfdPanel();
            }});
        </script>
    """

    return html, script


# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Iniciando procesamiento de datos...")
    path_excel = Path(ARCHIVO_ENTRADA)

    if not path_excel.exists():
        print(f"❌ Error: El archivo no existe en la ruta: {path_excel}")
        sys.exit(1)

    try:
        df_parque = cargar_parque_equipos(path_excel)
        df_int = cargar_intervenciones(path_excel)
        df_plan = cargar_plan_pm(path_excel, df_parque)
        df_kpis = cargar_kpis_consolidados(path_excel)

        generar_y_abrir_dashboard(df_kpis, df_int, df_plan, df_parque)

    except ErrorDatosFlota as e:
        print(str(e))
        print("⛔ Corrija la estructura del Excel de origen y vuelva a ejecutar.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado durante la generación del dashboard: {e}")
        sys.exit(1)