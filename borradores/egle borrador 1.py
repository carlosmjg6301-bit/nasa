"""Monitor de salud del astronauta (interfaz en Streamlit, estilo panel claro).

Datos simulados. Proyecto académico, no es un dispositivo médico.
Ejecutar:  pip install streamlit   y luego   streamlit run monitor_astronauta.py
"""
import streamlit as st

st.set_page_config(page_title="Monitor de salud del astronauta", layout="wide",
                   initial_sidebar_state="expanded")

# ---------- Paleta ----------
AZUL, CIAN = "#0A8CF0", "#00D9E6"
TEXTO, GRIS, SUAVE, AMBAR = "#2B3A4E", "#5F6B7A", "#E3E8EF", "#E39A00"
# estado -> (fondo del chip, texto del chip, color de la línea)
ESTADOS = {
    "Normal": ("#E0F5F2", "#0B6B63", AZUL),
    "Precaución": ("#FFF0D1", "#8A5A00", AMBAR),
    "Modo rápido": ("#E1EEFF", "#0B5FB3", AZUL),
}
NIVELES = {  # nivel de alerta -> (fondo, texto)
    "PRECAUCIÓN": ("#FFF0D1", "#8A5A00"),
    "REGLA": ("#1BD3E8FF", "#0B5FB3"),
    "INFO": ("#EEF1F5", GRIS),
}

# ---------- Datos simulados (en el proyecto real vendrían de los sensores) ----------
SERIES = {
    "sistolica": [117, 115, 118, 114, 117, 113, 116, 118],
    "fc": [62, 65, 61, 64, 60, 63, 62, 64],
    "glucosa": [100, 98, 97, 103, 106, 109, 112],
    "spo2": [98, 98, 97, 98, 99, 98, 98, 99],
    "temp": [37.0, 37.1, 37.0, 37.2, 37.1, 37.0, 37.1, 37.1],
    "sueno": [7.1, 6.8, 6.2, 6.1, 5.6, 5.8, 5.4],
    "rad_ext": [0.6, 0.6, 0.7, 0.9, 1.9, 2.1, 1.5, 1.38],
    "rad_cab": [0.50, 0.52, 0.51, 0.53, 0.50, 0.52, 0.51, 0.52],
    "linfocitos": [2010, 2000, 1960, 1930, 1900, 1880, 1860, 1850],
}
LINEA_BASE = {"sistolica": 117, "fc": 62, "linfocitos": 2010}
# Rangos ilustrativos: valídalos con fuentes oficiales antes de usarlos.
UMBRALES = {"sistolica": (90, 130), "fc": (50, 90), "temp": (36.0, 37.5), "glucosa": (70, 140)}
DOSIS_ACUMULADA, UMBRAL_DOSIS = 78, 100  # mSv, ejemplo
EN_SAA = True  # simula que la nave cruza la Anomalía del Atlántico Sur


# ---------- Reglas ----------
def estado_rango(valor, clave):
    minimo, maximo = UMBRALES[clave]
    return "Normal" if minimo <= valor <= maximo else "Precaución"


def noches_bajas(horas, limite=6.0):
    """Noches seguidas (hasta la más reciente) con menos de `limite` horas."""
    n = 0
    for h in reversed(horas):
        if h >= limite:
            break
        n += 1
    return n


def dias_en_ascenso(serie):
    """Días seguidos (hasta el más reciente) en que el valor fue subiendo."""
    n, i = 0, len(serie) - 1
    while i > 0 and serie[i] > serie[i - 1]:
        n, i = n + 1, i - 1
    return n


def evaluar_tormenta_solar(rad_exterior):
    """TODO (tuyo): decide cuándo se dispara el protocolo de tormenta solar.

    Recibe la lista de tasas de dosis exterior (mSv/día), de la más antigua a la
    más reciente, y devuelve True si hay que activar el protocolo.
    """
    return False


# ---------- Componentes visuales ----------
def cabecera(titulo, estado):
    fondo, texto, _ = ESTADOS[estado]
    return (f'<div class="fila"><span class="titulo">{titulo}</span>'
            f'<span class="chip" style="background:{fondo};color:{texto}">{estado}</span></div>')


def sparkline(serie, color):
    lo, hi = min(serie), max(serie)
    rango = (hi - lo) or 1
    n = len(serie) - 1
    pts = " ".join(f"{i * 100 / n:.0f},{26 - (v - lo) / rango * 22:.0f}" for i, v in enumerate(serie))
    return (f'<svg viewBox="0 0 100 28" style="width:100%;height:40px" aria-hidden="true">'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/></svg>')


def tarjeta(titulo, valor, unidad, estado, serie, nota, info_tooltip="Información del parámetro"):
    borde = ESTADOS[estado][2]
    return (f'<div class="card" style="border-color:{borde}" title="{info_tooltip}">'
            f'<div class="fila"><span class="gris">{titulo} ℹ️</span>'
            f'<span class="chip" style="background:{ESTADOS[estado][0]};color:{ESTADOS[estado][1]}">'
            f'{estado}</span></div>'
            f'<div><span class="valor">{valor}</span> <span class="nota">{unidad}</span></div>'
            f'{sparkline(serie, ESTADOS[estado][2])}<span class="nota">{nota}</span></div>')


def tarjeta_azul(dia, sensores, total):
    return (f'<div class="card" style="background:{AZUL};border-color:{AZUL};color:#fff;'
            f'flex-direction:row;gap:24px;align-items:center;justify-content:space-around">'
            f'<div><div style="font-size:36px;font-weight:700">{dia}</div>'
            f'<div class="titulo" style="color:#fff">DÍA DE MISIÓN</div></div>'
            f'<div><div style="font-size:36px;font-weight:700">{sensores}/{total}</div>'
            f'<div class="titulo" style="color:#fff">SENSORES</div>'
            f'<div style="height:4px;background:rgba(255,255,255,.35);border-radius:2px;margin-top:6px">'
            f'<div style="width:{sensores / total * 100:.0f}%;height:4px;background:#fff;border-radius:2px">'
            f'</div></div></div></div>')


def gauge(pct, titulo, estado, nota):
    r = 40
    c = 2 * 3.1416 * r
    return (f'<div style="text-align:center"><svg viewBox="0 0 100 100" style="width:130px" aria-hidden="true">'
            f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{SUAVE}" stroke-width="8"/>'
            f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{ESTADOS[estado][2]}" stroke-width="8" '
            f'stroke-linecap="round" stroke-dasharray="{c * min(pct, 100) / 100:.1f} {c:.1f}" '
            f'transform="rotate(-90 50 50)"/>'
            f'<text x="50" y="57" text-anchor="middle" font-size="20" font-weight="700" fill="{TEXTO}">'
            f'{pct:.0f}%</text></svg><div class="titulo">{titulo}</div><div class="nota">{nota}</div></div>')


def tarjeta_gauges(gauges):
    return (f'<div class="card" style="gap:22px;height:100%;justify-content:space-around">'
            f'{"".join(gauges)}</div>')


def tarjeta_barras(titulo, valor, unidad, estado, serie, nota):
    tope = max(serie)
    barras = "".join(
        f'<div style="flex:1;height:90px;background:{SUAVE};border-radius:6px;display:flex;align-items:flex-end">'
        f'<div style="width:100%;height:{v / tope * 100:.0f}%;border-radius:6px;'
        f'background:linear-gradient(180deg,{CIAN},{AZUL})"></div></div>' for v in serie)
    return (f'<div class="card">{cabecera(titulo, estado)}'
            f'<div><span class="valor">{valor}</span> <span class="nota">{unidad}</span></div>'
            f'<div style="display:flex;gap:6px">{barras}</div><span class="nota">{nota}</span></div>')


def tarjeta_tejido(acumulada, tejidos):
    estado = "Normal" if acumulada < UMBRAL_DOSIS else "Precaución"
    tope = max(tejidos.values())
    filas = "".join(
        f'<div><div class="fila"><span class="titulo">{t}</span><span class="azul">{d:.2f} mSv/día</span></div>'
        f'<div style="height:6px;background:{SUAVE};border-radius:3px;margin-top:4px">'
        f'<div style="width:{d / tope * 100:.0f}%;height:6px;border-radius:3px;'
        f'background:linear-gradient(90deg,{AZUL},{CIAN})"></div></div></div>' for t, d in tejidos.items())
    return (f'<div class="card">{cabecera("Reacción del tejido humano", estado)}'
            f'<div><span class="valor">{acumulada}</span> <span class="nota">mSv efectivos acumulados</span></div>'
            f'{filas}<span class="nota">Estimado con Q(LET) · D y pesos por tejido</span></div>')


def grafica_sueno(horas, limite=6.0):
    alto, lo, hi = 120, 4.0, 8.0
    y = lambda h: 15 + alto - (h - lo) / (hi - lo) * alto
    n = len(horas) - 1
    xs = [i * 400 / n for i in range(n + 1)]
    rejilla = "".join(f'<line x1="0" x2="400" y1="{y(h):.0f}" y2="{y(h):.0f}" stroke="{SUAVE}"/>'
                      for h in range(4, 9))
    pts = " ".join(f"{x:.0f},{y(h):.0f}" for x, h in zip(xs, horas))
    puntos = "".join(
        f'<circle cx="{x:.0f}" cy="{y(h):.0f}" r="5" fill="#fff" stroke-width="2.5" '
        f'stroke="{AMBAR if h < limite else CIAN}"/>' for x, h in zip(xs, horas))
    return (f'<svg viewBox="-10 0 420 150" style="width:100%" role="img" aria-label="Horas de sueño, 7 días">'
            f'{rejilla}<line x1="0" x2="400" y1="{y(limite):.0f}" y2="{y(limite):.0f}" stroke="{AMBAR}" '
            f'stroke-dasharray="5 4"/><polyline points="{pts}" fill="none" stroke="{CIAN}" stroke-width="2.5" '
            f'stroke-linejoin="round"/>{puntos}</svg>')


def grilla(tarjetas, minimo=200):
    return (f'<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax({minimo}px,1fr))">'
            f'{"".join(tarjetas)}</div>')


def seccion(texto, id_, color=TEXTO):
    st.markdown(f'<h2 id="{id_}" class="seccion" style="color:{color}">{texto}</h2>', unsafe_allow_html=True)


def titulo_seccion(texto, id_="estado-protocolos", color=TEXTO):
    seccion(texto, id_, color)


# ---------- Estilos ----------
st.markdown("""
<style>
.stApp{background:#EEF1F5;font-family:'Inter',system-ui,sans-serif;color:#2B3A4E}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1400px;padding-top:1rem}
section[data-testid="stSidebar"]{background:#fff;border-right:1px solid #E3E8EF}
.nav a{display:flex;align-items:center;gap:12px;padding:10px 4px;color:#0B6FC2;
       text-decoration:none;font-size:14px;font-weight:500}
.nav svg{width:20px;height:20px;fill:#0A8CF0;flex:none}
.barra{background:linear-gradient(90deg,#0A8CF0,#00D9E6);border-radius:3px;padding:14px 22px;
       display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
.card{background:#fff;border:1px solid #E3E8EF;border-radius:3px;padding:16px;
      box-shadow:0 2px 8px rgba(30,60,100,.12);display:flex;flex-direction:column;gap:8px}
.gris{color:#5F6B7A}
.grid{display:grid;gap:16px}
.fila{display:flex;justify-content:space-between;align-items:center;gap:8px}
.titulo{font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#2B3A4E}
.nota{font-size:12px;color:#5F6B7A}
.valor{font-size:34px;font-weight:700;color:#5F6B7A}
.azul{font-size:13px;font-weight:700;color:#0B6FC2}
.chip{font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px}
.seccion{font-size:13px;font-weight:700;letter-spacing:.08em;margin:26px 0 12px;padding:0}
.alerta{display:flex;gap:12px;padding:10px 12px;border-radius:3px;font-size:14px}
.alerta b{font-size:11px;min-width:84px}
</style>
""", unsafe_allow_html=True)

# ---------- Barra lateral ----------
ICONOS = {
    "Panel": "M3 11l9-8 9 8v10h-6v-6H9v6H3z",
    "Vitales": "M4 20V10h4v10zM10 20V4h4v16zM16 20v-7h4v7z",
    "Radiación": "M12 2a10 10 0 100 20 10 10 0 000-20zm0 6a4 4 0 110 8 4 4 0 010-8z",
    "Alertas": "M12 22a2 2 0 002-2h-4a2 2 0 002 2zm6-6V11a6 6 0 10-12 0v5l-2 2v1h16v-1z",
    "Protocolos": "M12 2l8 3v6c0 5-3.5 9.5-8 11-4.5-1.5-8-6-8-11V5z",
}
ANCLAS = {"Panel": "panel", "Vitales": "vitales", "Radiación": "radiacion",
          "Alertas": "alertas", "Protocolos": "protocolos"}
with st.sidebar:
    st.markdown('<div class="nav" style="margin-top:24px">' + "".join(
        f'<a href="#{ANCLAS[n]}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg>{n}</a>'
        for n, d in ICONOS.items()) + '</div>', unsafe_allow_html=True)
    st.markdown('<p class="nota" style="margin-top:32px">Modo autónomo · sin conexión<br>'
                'Última sincronización 08:30</p>', unsafe_allow_html=True)

# ---------- Encabezado ----------
st.markdown(
    '<div id="panel" class="barra"><span style="color:#fff;font-size:18px">MONITOR DE '
    '<b>SALUD DEL ASTRONAUTA</b></span>'
    '<span style="color:#06304D;font-size:13px;font-weight:600">Datos simulados · Proyecto académico</span></div>',
    unsafe_allow_html=True)

if evaluar_tormenta_solar(SERIES["rad_ext"]):
    st.error("Protocolo de tormenta solar activado")

# ---------- Panel de estado y protocolos ----------
S = SERIES
n_gluc = dias_en_ascenso(S["glucosa"])
estado_fc = estado_rango(S["fc"][-1], "fc")
estado_glucosa = estado_rango(S["glucosa"][-1], "glucosa")
estado_spo2 = "Normal" if S["spo2"][-1] >= 95 else "Precaución"
estado_temp = estado_rango(S["temp"][-1], "temp")

titulo_seccion("PANEL DE ESTADO Y PROTOCOLOS")
col_lateral, col_central = st.columns([1, 2.5])
with col_lateral:
    st.markdown(grilla([
        tarjeta("Frecuencia cardíaca", S["fc"][-1], "lpm", estado_fc, S["fc"],
                "Reposo · línea base personal: 62 lpm",
                "Frecuencia cardíaca medida por el sensor de pulso."),
        tarjeta("Glucosa", S["glucosa"][-1], "mg/dL", estado_glucosa, S["glucosa"],
                f"Tendencia: en ascenso {n_gluc} días",
                "Nivel de glucosa capilar simulado."),
        tarjeta("SpO2", S["spo2"][-1], "%", estado_spo2, S["spo2"],
                "Saturación de oxígeno en sangre",
                "Saturación periférica de oxígeno."),
        tarjeta("Temperatura", S["temp"][-1], "°C", estado_temp, S["temp"],
                "Cabina: 22.5 °C",
                "Temperatura corporal del astronauta."),
    ], minimo=180), unsafe_allow_html=True)
with col_central:
    st.markdown(
        '<div class="card" style="min-height:400px">'
        '<h2 style="margin:0;color:#2B3A4E">PROTOCOLO ACTIVO: ESTADO NOMINAL</h2>'
        '<p style="font-size:15px">Recomendaciones actuales: mantener el monitoreo de signos vitales, '
        'confirmar la sincronización de sensores y continuar con el muestreo programado.</p>'
        '<div class="alerta" style="background:#E0F5F2;color:#0B6B63">'
        '<b>ESTADO</b><span>Todos los parámetros prioritarios están dentro de los rangos ilustrativos.</span>'
        '</div></div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div class="card"><span class="titulo">GRÁFICAS DE RADIACIÓN · AMBIENT &amp; EXTERNAL</span>'
        '<div style="display:flex;gap:16px;flex-wrap:wrap">'
        f'<div style="flex:1;min-width:220px">{tarjeta_barras("External", S["rad_ext"][-1], "mSv/día", "Modo rápido" if EN_SAA else "Normal", S["rad_ext"], "Radiación exterior")}</div>'
        f'<div style="flex:1;min-width:220px">{tarjeta("Ambient", S["rad_cab"][-1], "mSv/día", "Normal", S["rad_cab"], "Radiación en cabina", "Radiación ambiental dentro de la cabina.")}</div>'
        '</div></div>',
        unsafe_allow_html=True)

# ---------- Parámetros vitales ----------
n_sueno = noches_bajas(S["sueno"])
estado_sueno = "Precaución" if n_sueno >= 3 else "Normal"

seccion("PARÁMETROS VITALES", "vitales")
st.markdown(grilla([
    tarjeta("Presión sanguínea", f'{S["sistolica"][-1]}/76', "mmHg",
            estado_rango(S["sistolica"][-1], "sistolica"), S["sistolica"],
            f'Línea base personal: {LINEA_BASE["sistolica"]}/75'),
    tarjeta("Frecuencia cardiaca", S["fc"][-1], "lpm · reposo",
            estado_rango(S["fc"][-1], "fc"), S["fc"], f'Línea base personal: {LINEA_BASE["fc"]} lpm'),
    tarjeta("Azúcar en la sangre", S["glucosa"][-1], "mg/dL",
            "Precaución" if n_gluc >= 3 or estado_rango(S["glucosa"][-1], "glucosa") != "Normal" else "Normal",
            S["glucosa"], f"Tendencia: en ascenso {n_gluc} días"),
    tarjeta("Temperatura corporal", S["temp"][-1], "°C",
            estado_rango(S["temp"][-1], "temp"), S["temp"], "Cabina: 22.5 °C"),
    tarjeta("Horas de sueño", S["sueno"][-1], "h anoche", estado_sueno, S["sueno"],
            f"{n_sueno} noches seguidas por debajo de 6 h"),
    tarjeta_azul(142, 3, 4),
]), unsafe_allow_html=True)

# ---------- Radiación ----------
caida = (LINEA_BASE["linfocitos"] - S["linfocitos"][-1]) / LINEA_BASE["linfocitos"] * 100
estado_linf = "Precaución" if caida > 5 else "Normal"

seccion("PARÁMETROS ESPECIALES · RADIACIÓN", "radiacion")
col_gauges, col_rad = st.columns([1, 3])
with col_gauges:
    st.markdown(tarjeta_gauges([
        gauge(DOSIS_ACUMULADA / UMBRAL_DOSIS * 100, "Dosis acumulada",
              "Normal" if DOSIS_ACUMULADA < UMBRAL_DOSIS else "Precaución",
              f"{DOSIS_ACUMULADA} de {UMBRAL_DOSIS} mSv (umbral de ejemplo)"),
        gauge(S["linfocitos"][-1] / LINEA_BASE["linfocitos"] * 100, "Linfocitos", estado_linf,
              f'{S["linfocitos"][-1]:,} células/µL · {caida:.0f}% bajo su línea base'),
    ]), unsafe_allow_html=True)
with col_rad:
    st.markdown(grilla([
        tarjeta_barras("Radiación exterior", S["rad_ext"][-1], "mSv/día",
                       "Modo rápido" if EN_SAA else "Normal", S["rad_ext"],
                       "Anomalía del Atlántico Sur · muestreo cada 20 s" if EN_SAA else "Muestreo cada 90 s"),
        tarjeta("Radiación en cabina", S["rad_cab"][-1], "mSv/día", "Normal", S["rad_cab"],
                "Flujo: 0.8 partículas/(s·cm²) · muestreo cada 90 s"),
        tarjeta_tejido(DOSIS_ACUMULADA, {"Piel": 0.90, "Médula ósea": 0.60, "Cristalino": 0.80}),
    ], minimo=250), unsafe_allow_html=True)

# ---------- Sueño y alertas ----------
alertas = []
if n_sueno >= 3:
    alertas.append(("PRECAUCIÓN", f"Sueño por debajo de 6 h durante {n_sueno} noches seguidas."))
if n_gluc >= 3:
    alertas.append(("PRECAUCIÓN", "Glucosa en ascenso sostenido respecto a la línea base."))
if n_sueno >= 3 and n_gluc >= 3:
    alertas.append(("REGLA", "Patrón combinado: poco sueño y glucosa al alza. Se recomienda revisar el protocolo."))
if caida > 5:
    alertas.append(("PRECAUCIÓN", f"Linfocitos {caida:.0f}% por debajo de su línea base."))
alertas.append(("INFO", "Sensor sin datos de 22:00 a 23:10. Lecturas marcadas como no válidas."))

seccion("SUEÑO Y ALERTAS", "alertas")
col_sueno, col_alertas = st.columns([2, 1])
with col_sueno:
    st.markdown(
        f'<div class="card" style="height:100%">{cabecera("Sueño de los últimos 7 días", estado_sueno)}'
        f'<div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap">'
        f'<div style="flex:1;min-width:260px">{grafica_sueno(S["sueno"])}'
        f'<div class="fila nota"><span>Hace 7 días</span><span>Línea punteada: 6 h</span><span>Anoche</span></div></div>'
        f'<div><div class="titulo">Noches bajas</div><div class="valor" style="color:{AZUL}">{n_sueno}</div>'
        f'<div class="titulo" style="margin-top:12px">Anoche</div>'
        f'<div class="valor" style="color:{AZUL}">{S["sueno"][-1]} h</div></div></div></div>',
        unsafe_allow_html=True)
with col_alertas:
    st.markdown(
        f'<div class="card" style="height:100%"><span class="titulo">Alertas activas</span>' + "".join(
            f'<div class="alerta" style="background:{NIVELES[n][0]}">'
            f'<b style="color:{NIVELES[n][1]}">{n}</b><span>{t}</span></div>' for n, t in alertas)
        + '</div>', unsafe_allow_html=True)

# ---------- Protocolos de emergencia ----------
PROTOCOLOS = [
    ("Tormenta solar", "salto brusco de la tasa de dosis exterior.",
     ["Pasar a modo rápido (muestreo cada 20 s).",
      "Suspender actividades fuera de la nave e ir al refugio blindado.",
      "Registrar la dosis cada 15 min hasta que baje."]),
    ("Descompresión o hipoxia", "SpO2 bajo o caída de presión en cabina.",
     ["Colocar el equipo de oxígeno y verificar sensores.",
      "Aislar el módulo afectado.",
      "Mantener reposo y revisar signos vitales cada 5 min."]),
    ("Emergencia cardiovascular", "presión o pulso fuera de su línea base en reposo.",
     ["Detener el ejercicio y mantener reposo.",
      "Repetir la medición con un segundo sensor.",
      "Abrir la guía médica autónoma y anotar en la bitácora."]),
    ("Falla de sensores o energía", "lecturas inválidas o sensor sin datos.",
     ["Cambiar al sensor de respaldo.",
      "Guardar los datos en memoria local.",
      "Marcar el periodo como no válido y reintentar."]),
]

seccion("PROTOCOLOS DE EMERGENCIA", "protocolos", color="#B3283A")
st.caption("Pasos de ejemplo. Deben validarse con los protocolos oficiales.")
for col, (nombre, disparador, pasos) in zip(st.columns(len(PROTOCOLOS)), PROTOCOLOS):
    with col:
        lista = "".join(f"<li>{p}</li>" for p in pasos)
        st.markdown(
            f'<div class="card" style="border-top:3px solid #D64550;min-height:260px">'
            f'<span class="titulo">{nombre}</span>'
            f'<p style="margin:0;font-size:13px;color:#B3283A">Disparador: {disparador}</p>'
            f'<ol style="margin:0;padding-left:20px;font-size:14px;line-height:1.5">{lista}</ol></div>',
            unsafe_allow_html=True)
        if st.button("Abrir protocolo", key=nombre):
            st.toast(f"Protocolo abierto: {nombre}")

st.markdown('<p class="nota" style="margin-top:24px">Interfaz de ejemplo con datos simulados. '
            'Proyecto académico, no es un dispositivo médico.</p>', unsafe_allow_html=True)
