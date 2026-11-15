"""Central de monitoreo EGLE conectada a SQLite y al motor médico determinista."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

import database_sim
import motor_medico as medico


st.set_page_config(page_title="EGLE · Central médica", layout="wide")

DB_PATH = database_sim.DB_PATH
FONDO = "#F4F7FA"
BLANCO = "#FFFFFF"
BORDES = "#DCE4EC"
AZUL = "#0A8CF0"
VERDE = "#0B6B63"
VERDE_FONDO = "#E0F5F2"
AMBAR = "#E39A00"
ROJO = "#D64550"
GRIS = "#5F6B7A"
TEXTO = "#2B3A4E"
ESTADO_COLOR = {
    medico.NOMINAL: VERDE,
    medico.PRECAUCION: AMBAR,
    medico.CRITICO: ROJO,
}
ESTADO_FONDO = {
    medico.NOMINAL: VERDE_FONDO,
    medico.PRECAUCION: "#FFF4D6",
    medico.CRITICO: "#FDE8EA",
}

PARAMETROS = {
    "Radiación": "radiacion_externa",
    "HR": "frecuencia_cardiaca",
    "Blood Sugar": "glucosa_cgm",
    "SpO2": "spo2",
    "Temperatura": "temperatura_corporal",
    "Sueño": "sueno_fatiga",
    "Densidad Ósea / Orina": "calcio_urinario_densidad_osea",
}


def conexion() -> sqlite3.Connection:
    database_sim.crear_esquema()
    if not DB_PATH.exists():
        database_sim.inicializar_datos()
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def cargar_tripulacion(db: sqlite3.Connection) -> list[sqlite3.Row]:
    filas = db.execute(
        "SELECT * FROM tripulacion ORDER BY id_astronauta"
    ).fetchall()
    if not filas:
        database_sim.inicializar_datos()
        return cargar_tripulacion(conexion())
    return filas


def cargar_datos(db: sqlite3.Connection, astronauta_id: int) -> tuple[list[sqlite3.Row], list[sqlite3.Row]]:
    telemetria = db.execute(
        """
        SELECT * FROM telemetria_continua
        WHERE id_astronauta = ?
        ORDER BY timestamp
        """,
        (astronauta_id,),
    ).fetchall()
    discretos = db.execute(
        """
        SELECT * FROM registros_discretos
        WHERE id_astronauta = ?
        ORDER BY timestamp
        """,
        (astronauta_id,),
    ).fetchall()
    if not telemetria or not discretos:
        raise RuntimeError("No hay telemetría completa para el astronauta seleccionado")
    return telemetria, discretos


def hashes_verificados(db: sqlite3.Connection) -> bool:
    columnas = database_sim.TELEMETRIA_COLUMNAS
    filas = db.execute("SELECT * FROM telemetria_continua").fetchall()
    for fila in filas:
        valores = [fila[columna] for columna in columnas]
        contenido = json.dumps(valores, ensure_ascii=True, separators=(",", ":"))
        esperado = hashlib.sha256(contenido.encode("utf-8")).hexdigest()
        if esperado != fila["integrity_hash"]:
            return False
    return bool(filas)


def estado_color(estado: str) -> str:
    return ESTADO_COLOR.get(estado, GRIS)


def estado_fondo(estado: str) -> str:
    return ESTADO_FONDO.get(estado, "#EEF1F5")


def noches_bajas(serie: list[float], limite: float = 6.0) -> int:
    cantidad = 0
    for horas in reversed(serie):
        if horas > limite:
            break
        cantidad += 1
    return cantidad


def obtener_estados(
    actual: sqlite3.Row,
    discretos: sqlite3.Row,
    perfil: sqlite3.Row,
    historial: list[sqlite3.Row],
) -> dict[str, str]:
    sueno = [float(fila["sleep_hours"]) for fila in historial]
    return {
        "radiacion_externa": medico.evaluar_radiacion(
            actual["rad_ambient_msv"], actual["rad_external_msv"]
        ),
        "frecuencia_cardiaca": medico.evaluar_frecuencia_cardiaca(
            actual["heart_rate"], perfil["fc_reposo"]
        ),
        "glucosa_cgm": medico.evaluar_glucosa(actual["glucose_cgm"]),
        "spo2": medico.evaluar_spo2(actual["spo2"]),
        "temperatura_corporal": medico.evaluar_temperatura(actual["body_temp"]),
        "sueno_fatiga": medico.evaluar_sueno_fatiga(
            actual["sleep_hours"], noches_bajas(sueno)
        ),
        "calcio_urinario_densidad_osea": medico.evaluar_calcio_urinario(
            discretos["urinary_calcium_mg_dl"]
        ),
    }


def serie_parametro(
    parametro: str, historial: list[sqlite3.Row], discretos: list[sqlite3.Row]
) -> tuple[list[float], str, str]:
    if parametro == "frecuencia_cardiaca":
        return [fila["heart_rate"] for fila in historial], "lpm", "heart_rate"
    if parametro == "glucosa_cgm":
        return [fila["glucose_cgm"] for fila in historial], "mg/dL", "glucose_cgm"
    if parametro == "spo2":
        return [fila["spo2"] for fila in historial], "%", "spo2"
    if parametro == "temperatura_corporal":
        return [fila["body_temp"] for fila in historial], "°C", "body_temp"
    if parametro == "sueno_fatiga":
        return [fila["sleep_hours"] for fila in historial], "h", "sleep_hours"
    if parametro == "calcio_urinario_densidad_osea":
        return (
            [fila["urinary_calcium_mg_dl"] for fila in discretos],
            "mg/dL",
            "urinary_calcium_mg_dl",
        )
    return [fila["rad_external_msv"] for fila in historial], "mSv/día", "rad_external_msv"


def formula_aplicada(
    parametro: str,
    actual: sqlite3.Row,
    anterior: sqlite3.Row,
    discreto: sqlite3.Row,
    perfil: sqlite3.Row,
) -> tuple[str, str]:
    if parametro == "frecuencia_cardiaca":
        calculo = medico.calcular_hr(actual["rr_interval_sec"])
        return "HR = 60 / RR_interval", f"60 / {actual['rr_interval_sec']:.4f} s = {calculo:.2f} lpm"
    if parametro == "presion_arterial":
        calculo = medico.calcular_map(actual["sbp"], actual["dbp"])
        return "MAP = DBP + (SBP - DBP) / 3", f"{actual['dbp']:.1f} + ({actual['sbp']:.1f} - {actual['dbp']:.1f}) / 3 = {calculo:.2f} mmHg"
    if parametro == "glucosa_cgm":
        delta = actual["glucose_cgm"] - anterior["glucose_cgm"]
        return "tendencia = (actual - anterior) / intervalo_min", f"({actual['glucose_cgm']:.1f} - {anterior['glucose_cgm']:.1f}) / 1 min = {delta:.2f} mg/dL/min"
    if parametro == "spo2":
        return "SpO2 = (HbO2 / (HbO2 + Hb)) * 100", f"lectura calibrada del oxímetro = {actual['spo2']:.1f}%"
    if parametro == "temperatura_corporal":
        return "T_corporal = lectura calibrada del sensor", f"lectura calibrada = {actual['body_temp']:.2f} °C"
    if parametro == "sueno_fatiga":
        return "horas_sueño = fin_sueño - inicio_sueño", f"duración registrada = {actual['sleep_hours']:.2f} h"
    if parametro == "calcio_urinario_densidad_osea":
        return "riesgo = calcio_urinario / línea_base_calcio", f"{discreto['urinary_calcium_mg_dl']:.2f} / 9.50 = {discreto['urinary_calcium_mg_dl'] / 9.5:.2f}x"
    dosis = medico.calcular_dosis_equivalente_efectiva(1.0, actual["rad_external_msv"])
    return "Dosis equivalente efectiva = Q(LET) * D", f"1.0 * {actual['rad_external_msv']:.4f} = {dosis:.4f} mSv/día"


def grafica_svg(serie: list[float], color: str) -> str:
    minimo, maximo = min(serie), max(serie)
    rango = maximo - minimo or 1.0
    divisor = max(len(serie) - 1, 1)
    puntos = " ".join(
        f"{i * 420 / divisor:.0f},{120 - (valor - minimo) / rango * 100:.0f}"
        for i, valor in enumerate(serie)
    )
    return (
        f'<svg viewBox="0 0 420 140" role="img" aria-label="Histórico del parámetro" '
        f'style="width:100%;height:180px;background:#F8FAFC;border-radius:8px">'
        f'<line x1="0" y1="120" x2="420" y2="120" stroke="{BORDES}"/>'
        f'<polyline points="{puntos}" fill="none" stroke="{color}" stroke-width="4" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def atlas_svg(estados: dict[str, str]) -> str:
    def color(key: str) -> str:
        return estado_color(estados.get(key, medico.NOMINAL))

    return f"""
    <div class="atlas">
      <svg viewBox="0 0 320 450" role="img" aria-label="Atlas corporal interactivo">
        <circle cx="160" cy="48" r="29" fill="#F8FAFC" stroke="{BORDES}" stroke-width="3"/>
        <path d="M142 78 L178 78 L202 145 L190 270 L218 390 M178 145 L102 190 L78 290 M142 145 L218 190 L242 290 M142 270 L112 410 M178 270 L208 410"
              fill="none" stroke="{BORDES}" stroke-width="12" stroke-linecap="round"/>
        <circle cx="151" cy="43" r="9" fill="{color('sueno_fatiga')}"/>
        <circle cx="169" cy="43" r="9" fill="{color('spo2')}"/>
        <circle cx="160" cy="123" r="11" fill="{color('frecuencia_cardiaca')}"/>
        <circle cx="160" cy="205" r="11" fill="{color('glucosa_cgm')}"/>
        <circle cx="139" cy="250" r="10" fill="{color('calcio_urinario_densidad_osea')}"/>
        <circle cx="181" cy="250" r="10" fill="{color('calcio_urinario_densidad_osea')}"/>
        <text x="202" y="46" class="atlas-label">Cerebro / sueño</text>
        <text x="202" y="86" class="atlas-label">Ojos / SpO2</text>
        <text x="202" y="126" class="atlas-label">Corazón / HR</text>
        <text x="202" y="208" class="atlas-label">Páncreas / glucosa</text>
        <text x="202" y="253" class="atlas-label">Riñones / huesos</text>
      </svg>
    </div>
    """


def tarjeta_parametro(nombre: str, estado: str, valor: str) -> str:
    color = estado_color(estado)
    return (
        f'<div class="parameter-card" style="border-left-color:{color}">'
        f'<span>{escape(nombre)}</span><b style="color:{color}">{escape(valor)}</b></div>'
    )


st.markdown(
    f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{ background:{FONDO}; color:{TEXTO}; }}
    .block-container {{ max-width:1500px; padding-top:1.2rem; }}
    header[data-testid="stHeader"] {{ background:transparent; }}
    .topbar {{ background:{BLANCO}; border:1px solid {BORDES}; border-radius:12px;
               padding:16px 22px; box-shadow:0 2px 8px rgba(30,60,100,.08); }}
    .card {{ background:{BLANCO}; border:1px solid {BORDES}; border-radius:10px;
             padding:18px; box-shadow:0 2px 8px rgba(30,60,100,.08); margin-bottom:14px; }}
    .parameter-card {{ background:{BLANCO}; border:1px solid {BORDES}; border-left:5px solid;
                       border-radius:8px; padding:11px 12px; margin-bottom:8px;
                       display:flex; justify-content:space-between; gap:8px; }}
    .parameter-card span {{ color:{TEXTO}; font-size:12px; font-weight:700; }}
    .section-title {{ color:{TEXTO}; font-size:13px; letter-spacing:.08em; font-weight:800;
                      margin:16px 0 10px; }}
    .atlas-label {{ fill:{GRIS}; font-size:10px; font-family:Arial,sans-serif; }}
    .formula {{ background:#F8FAFC; border:1px solid {BORDES}; border-radius:8px;
                padding:12px; font-family:Consolas,monospace; color:{TEXTO}; }}
    .help {{ color:{GRIS}; font-size:13px; line-height:1.45; }}
    h1, h2, h3 {{ color:{TEXTO}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


with conexion() as db:
    tripulacion = cargar_tripulacion(db)
    nombres = [fila["nombre"] for fila in tripulacion]
    st.markdown(
        '<div class="topbar"><h1 style="margin:0;color:#2B3A4E">EGLE · CENTRAL DE MONITOREO</h1>'
        '<p style="margin:4px 0 0;color:#5F6B7A">NASA-STD-3001 / HRP · lógica determinista · operación offline</p></div>',
        unsafe_allow_html=True,
    )
    col_astronauta, col_capa, col_integridad = st.columns([2, 1.3, 2])
    with col_astronauta:
        nombre = st.selectbox("Astronauta", nombres)
    with col_capa:
        capa = st.selectbox("Capa", ["HB", "AMBIENT", "EXTERNAL"], format_func=lambda value: {
            "HB": "HB · Cuerpo Humano",
            "AMBIENT": "AMBIENT · Cabina",
            "EXTERNAL": "EXTERNAL · Exterior / EVA",
        }[value])
    with col_integridad:
        integridad = hashes_verificados(db)
        etiqueta = "SQLite Offline · Anti-SEU Hash Verificado" if integridad else "SQLite Offline · Hash no verificado"
        color = VERDE if integridad else ROJO
        st.markdown(
            f'<div style="margin-top:28px;padding:10px;border-radius:8px;background:{VERDE_FONDO if integridad else "#FDE8EA"};color:{color};font-weight:700;text-align:center">{etiqueta}</div>',
            unsafe_allow_html=True,
        )

    perfil = next(fila for fila in tripulacion if fila["nombre"] == nombre)

    with st.sidebar:
        st.markdown("### DEMOSTRACIÓN EN VIVO")
        if st.button("Simular avance de misión en vivo", use_container_width=True):
            database_sim.insertar_lectura_en_vivo(perfil["id_astronauta"])
            st.rerun()

        st.markdown("### SIMULACIÓN DE EMERGENCIA")
        if st.button("Emergencia EVA · Hipoxia", use_container_width=True):
            database_sim.insertar_lectura_en_vivo(
                perfil["id_astronauta"],
                spo2=88.0,
            )
            st.session_state.emergency_banner = {
                "tipo": "HIPoxia DURANTE EVA",
                "astronauta": nombre,
                "detalle": "SpO2 crítica detectada: 88%.",
            }
            st.rerun()
        if st.button("Tormenta solar · EVA", use_container_width=True):
            database_sim.insertar_lectura_en_vivo(
                perfil["id_astronauta"],
                rad_ambient_msv=1.8,
                rad_external_msv=3.5,
            )
            st.session_state.emergency_banner = {
                "tipo": "TORMENTA SOLAR",
                "astronauta": nombre,
                "detalle": "Flujo externo crítico detectado: 3.5 mSv/día.",
            }
            st.rerun()

    ultimo_discreto = db.execute(
        """
        SELECT * FROM registros_discretos
        WHERE id_astronauta = ?
        ORDER BY timestamp DESC LIMIT 1
        """,
        (perfil["id_astronauta"],),
    ).fetchone()
    if ultimo_discreto is None:
        raise RuntimeError("No existe un registro discreto inicial para el astronauta")

    with st.expander("BITÁCORA CLÍNICA · DATOS NO CONTINUOS", expanded=False):
        st.caption("Registro manual/periódico. Los datos se guardan directamente en SQLite.")
        with st.form("bitacora_clinica"):
            calcio_manual = st.number_input(
                "Calcio en orina (mg/dL)",
                min_value=0.0,
                max_value=100.0,
                value=float(ultimo_discreto["urinary_calcium_mg_dl"]),
                step=0.1,
            )
            winscat_manual = st.number_input(
                "Resultado cognitivo WinSCAT",
                min_value=0.0,
                max_value=100.0,
                value=float(ultimo_discreto["winscat_cognitive_score"]),
                step=0.1,
            )
            mood_manual = st.selectbox(
                "Estado de ánimo",
                ["Nominal", "Estable", "Fatiga", "Vigilancia", "Ansiedad"],
                index=0,
            )
            guardar_bitacora = st.form_submit_button("Guardar en bitácora")
        if guardar_bitacora:
            db.execute(
                """
                INSERT INTO registros_discretos
                    (id_astronauta, timestamp, urinary_calcium_mg_dl,
                     lymphocytes_count, winscat_cognitive_score, mood_status)
                VALUES (?, datetime('now'), ?, ?, ?, ?)
                """,
                (
                    perfil["id_astronauta"],
                    calcio_manual,
                    ultimo_discreto["lymphocytes_count"],
                    winscat_manual,
                    mood_manual,
                ),
            )
            db.commit()
            st.rerun()

    emergency = st.session_state.get("emergency_banner")
    if emergency:
        st.markdown(
            f"""
            <div style="background:#FDE8EA;border:3px solid {ROJO};border-radius:10px;
                        padding:18px 22px;margin:16px 0;color:#7D1E2B">
              <h2 style="margin:0;color:{ROJO}">⚠️ SOBRESCRITURA DE EMERGENCIA · {emergency["tipo"]}</h2>
              <p style="font-weight:700;margin:6px 0 14px">{escape(emergency["astronauta"])} · {escape(emergency["detalle"])}</p>
              <div style="display:flex;gap:28px;flex-wrap:wrap">
                <div style="flex:1;min-width:280px">
                  <b>ASTRONAUTA AFECTADO</b>
                  <ol><li>Abortar EVA, asegurar el cordón y regresar al refugio presurizado.</li>
                      <li>Usar oxígeno al 100% según el procedimiento autorizado y repetir SpO2.</li>
                      <li>Reportar estado y lectura al control de misión inmediatamente.</li></ol>
                </div>
                <div style="flex:1;min-width:280px">
                  <b>TRIPULACIÓN EN CABINA</b>
                  <ol><li>Abrir el protocolo de retorno y preparar esclusa, oxígeno y compañero de rescate.</li>
                      <li>Trasladarse al refugio blindado durante la tormenta solar y asegurar la estiba.</li>
                      <li>Registrar dosis, tiempo y comunicaciones; mantener libre el canal médico.</li></ol>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Cerrar banner de emergencia", type="secondary"):
            del st.session_state["emergency_banner"]
            st.rerun()

    historial, discretos = cargar_datos(db, perfil["id_astronauta"])
    actual = historial[-1]
    anterior = historial[-2] if len(historial) > 1 else actual
    discreto = discretos[-1]
    estados = obtener_estados(actual, discreto, perfil, historial)

    if capa == "EXTERNAL":
        parametro_inicial = "Radiación"
    elif capa == "AMBIENT":
        parametro_inicial = "Temperatura"
    else:
        parametro_inicial = "HR"
    if "parametro_activo" not in st.session_state:
        st.session_state.parametro_activo = parametro_inicial

    izquierda, central, atlas = st.columns([1, 3.2, 1.35], gap="medium")
    with izquierda:
        st.markdown('<div class="section-title">PARÁMETRO ACTIVO</div>', unsafe_allow_html=True)
        valores = {
            "Radiación": f"{actual['rad_external_msv']:.2f} mSv/d",
            "HR": f"{actual['heart_rate']:.0f} lpm",
            "Blood Sugar": f"{actual['glucose_cgm']:.0f} mg/dL",
            "SpO2": f"{actual['spo2']:.0f}%",
            "Temperatura": f"{actual['body_temp']:.1f} °C",
            "Sueño": f"{actual['sleep_hours']:.1f} h",
            "Densidad Ósea / Orina": f"{discreto['urinary_calcium_mg_dl']:.1f} mg/dL",
        }
        for label, key in PARAMETROS.items():
            if st.button(label, key=f"param-{key}", use_container_width=True):
                st.session_state.parametro_activo = label
            st.markdown(tarjeta_parametro(label, estados[key], valores[label]), unsafe_allow_html=True)

    with central:
        activo = st.session_state.parametro_activo
        clave = PARAMETROS[activo]
        definicion = medico.MEDIDAS_MEDICAS[clave]
        serie, unidad, _ = serie_parametro(clave, historial, discretos)
        estado = estados[clave]
        medida = definicion["medida"]
        if clave == "radiacion_externa":
            valor_actual = actual["rad_external_msv"] if capa == "EXTERNAL" else actual["rad_ambient_msv"]
        elif clave == "frecuencia_cardiaca":
            valor_actual = actual["heart_rate"]
        elif clave == "glucosa_cgm":
            valor_actual = actual["glucose_cgm"]
        elif clave == "spo2":
            valor_actual = actual["spo2"]
        elif clave == "temperatura_corporal":
            valor_actual = actual["body_temp"]
        elif clave == "sueno_fatiga":
            valor_actual = actual["sleep_hours"]
        else:
            valor_actual = discreto["urinary_calcium_mg_dl"]
        ecuacion, calculo = formula_aplicada(clave, actual, anterior, discreto, perfil)
        color = estado_color(estado)
        st.markdown(
            f'<div class="card" style="border-top:5px solid {color}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div><div class="section-title" style="margin:0">{escape(activo)}</div>'
            f'<span class="help">{escape(medida["sensor"])} · {escape(medida["unidad"])}</span></div>'
            f'<span style="background:{estado_fondo(estado)};color:{color};padding:7px 12px;border-radius:99px;font-weight:800">{estado}</span>'
            f'</div><div style="font-size:48px;font-weight:800;color:{color};margin-top:16px">{valor_actual:.2f} <small style="font-size:18px;color:{GRIS}">{unidad}</small></div>'
            f'{grafica_svg(serie, color)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="card"><div class="section-title">2 · FÓRMULA MATEMÁTICA APLICADA</div>'
            f'<div class="formula">{escape(ecuacion)}<br><strong>{escape(calculo)}</strong></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="card" style="border-left:5px solid {color}"><div class="section-title">3 · UMBRAL ESPACIAL ❔</div>'
            f'<p class="help">Estado calculado por <b>{escape(clave)}</b>: <strong style="color:{color}">{estado}</strong>. '
            'En microgravedad, los desplazamientos de fluidos, la fatiga y la exposición a radiación pueden alterar la tolerancia fisiológica; '
            'por eso se compara la lectura con límites operacionales y la línea base individual.</p></div>',
            unsafe_allow_html=True,
        )
        pasos = "".join(f"<li>{escape(paso)}</li>" for paso in definicion["protocolo"])
        st.markdown(
            f'<div class="card"><div class="section-title">4 · PROTOCOLO Y RECOMENDACIONES</div>'
            f'<ol style="line-height:1.65;color:{TEXTO}">{pasos}</ol>'
            '<p class="help">Aplicar siempre el procedimiento oficial y confirmar con el control de misión.</p></div>',
            unsafe_allow_html=True,
        )

    with atlas:
        st.markdown('<div class="section-title">ATLAS CORPORAL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{atlas_svg(estados)}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card"><div class="section-title">CAPA {capa}</div>'
            f'<p class="help">Verde: nominal<br>Ámbar: precaución<br>Rojo: crítico</p>'
            f'<p class="help">Última lectura:<br>{escape(actual["timestamp"])}</p></div>',
            unsafe_allow_html=True,
        )

st.caption("Datos sintéticos para simulación. No es un dispositivo médico ni sustituye instrucciones de la tripulación.")
