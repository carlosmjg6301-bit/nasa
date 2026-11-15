import streamlit as st
import pandas as pd
import os
import config_medica as cfg  # Importa el archivo donde ustedes meten su investigación

st.set_page_config(page_title="EGLE Monitor", layout="wide", initial_sidebar_state="collapsed")

# Estilos claros: Blanco, Azul Aeroespacial y Verde Clínico
st.markdown("""
<style>
    .stApp { background-color: #F4F7FA; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem; max-width: 1380px; }
    .top-bar {
        background: linear-gradient(90deg, #0A8CF0 0%, #0284C7 100%);
        color: white; padding: 14px 24px; border-radius: 10px;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
    }
    .card {
        background: #FFFFFF; border: 1px solid #DCE4EC; border-radius: 12px;
        padding: 20px; box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04); margin-bottom: 14px;
    }
    .big-num { font-size: 68px; font-weight: 800; line-height: 1.05; margin: 10px 0; }
    div.stButton > button {
        width: 100%; text-align: left; justify-content: flex-start;
        background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px;
        padding: 12px 14px; font-weight: 600; color: #1E293B;
    }
    div.stButton > button:hover { border-color: #0A8CF0; color: #0A8CF0; background: #F0F9FF; }
</style>
""", unsafe_allow_html=True)

# Inicializar memoria temporal de lecturas en vivo (arranca con los valores de config_medica.py)
if "lecturas" not in st.session_state:
    st.session_state.lecturas = {
        astro: {param: info["valor_inicial"] for param, info in cfg.PARAMETROS.items()}
        for astro in cfg.ASTRONAUTAS
    }
if "param_seleccionado" not in st.session_state:
    st.session_state.param_seleccionado = list(cfg.PARAMETROS.keys())[0]

# Ventana emergente para mostrar la matemática sin saturar la pantalla
@st.dialog("📐 Fórmula Matemática y Justificación Científica")
def mostrar_detalle_cientifico(nombre_param, info_param):
    st.subheader(nombre_param)
    st.info(f"**Fórmula aplicada:** `{info_param['formula_texto']}`")
    st.warning(f"**Umbral de alerta espacial:** {info_param['umbral_texto']}")
    st.markdown(f"**Justificación fisiológica:**\n\n{info_param['justificacion']}")

# Encabezado superior
st.markdown("""
<div class="top-bar">
    <div><span style="font-size:20px; font-weight:800;">EGLE MONITOR</span>
    <span style="font-size:13px; opacity:0.9; margin-left:12px;">Sistema Autónomo de Telemetría Médica</span></div>
    <div style="font-size:12px; font-weight:600; background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:999px;">
        🟢 Operación Local · Offline-First
    </div>
</div>
""", unsafe_allow_html=True)

# Selectores globales de la Central
c_astro, c_capa = st.columns([1.2, 2])
with c_astro:
    astro_activo = st.selectbox("Tripulante activo:", list(cfg.ASTRONAUTAS.keys()), label_visibility="collapsed")
with c_capa:
    capa_activa = st.radio("Capa:", cfg.CAPAS, horizontal=True, label_visibility="collapsed")

# MENÚ DE APLICACIÓN (PESTAÑAS REALES)
tab_monitor, tab_central, tab_simulador, tab_docs = st.tabs([
    "🖥️ Monitor Principal (Pizarrón)",
    "👥 Central de Tripulación (Todos)",
    "🎛️ Simulador y Bitácora Manual",
    "📚 Fórmulas e Investigación"
])

# ==============================================================================
# PESTAÑA 1: MONITOR PRINCIPAL (DISEÑO DEL PIZARRÓN)
# ==============================================================================
with tab_monitor:
    col_menu, col_centro, col_atlas = st.columns([1.1, 2.3, 1.1], gap="medium")

    # 1. Columna Izquierda: Botones limpios (sin duplicar tarjetas)
    with col_menu:
        st.markdown("**PARÁMETROS**")
        for p_nombre, p_info in cfg.PARAMETROS.items():
            val = st.session_state.lecturas[astro_activo][p_nombre]
            estado, _ = cfg.evaluar_estado(p_nombre, val, cfg.ASTRONAUTAS[astro_activo])
            punto = {"NORMAL": "🟢", "PRECAUCIÓN": "🟡", "CRÍTICO": "🔴", "SIN DATOS": "⚪"}[estado]
            if st.button(f"{punto} {p_nombre} ({val} {p_info['unidad']})", key=f"nav_{p_nombre}"):
                st.session_state.param_seleccionado = p_nombre
                st.rerun()

    # Datos del parámetro activo
    p_act = st.session_state.param_seleccionado
    info_act = cfg.PARAMETROS[p_act]
    val_act = st.session_state.lecturas[astro_activo][p_act]
    estado_act, color_act = cfg.evaluar_estado(p_act, val_act, cfg.ASTRONAUTAS[astro_activo])

    # 2. Columna Central: Protocolo + Valor Gigante + Recomendaciones
    with col_centro:
        sub1, sub2 = st.columns([1.1, 1])
        with sub1:
            pasos_html = "".join([f"<p style='margin:6px 0; font-size:14px;'>{paso}</p>" for paso in info_act["protocolo"]])
            st.markdown(f"""
            <div class="card" style="min-height:270px; border-top:4px solid {color_act};">
                <div style="font-weight:800; font-size:16px; margin-bottom:8px;">📋 Protocolo de Acción</div>
                {pasos_html}
            </div>
            """, unsafe_allow_html=True)

        with sub2:
            st.markdown(f"""
            <div class="card" style="min-height:270px; text-align:center; display:flex; flex-direction:column; justify-content:center; border-top:4px solid {color_act};">
                <div style="font-size:12px; font-weight:700; color:{color_act};">● {estado_act} · {capa_activa}</div>
                <div style="font-size:18px; font-weight:700; color:#475569; margin-top:8px;">{p_act.upper()}</div>
                <div class="big-num" style="color:{color_act};">{val_act}</div>
                <div style="font-size:20px; font-weight:600; color:#64748B;">{info_act['unidad']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Botón para abrir la ventana emergente de fórmula y umbral
        if st.button("❓ Ver Fórmula Matemática, Umbral y Justificación", key="btn_modal"):
            mostrar_detalle_cientifico(p_act, info_act)

        st.markdown(f"""
        <div class="card" style="border-left:5px solid #0A8CF0; margin-top:10px;">
            <div style="font-weight:800; font-size:15px; margin-bottom:4px;">💡 Recomendaciones Operativas</div>
            <div style="font-size:14px; color:#334155;">{info_act['recomendaciones']}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Columna Derecha: Atlas Anatómico Estilizado (o imagen propia si existe cuerpo.png)
    with col_atlas:
        st.markdown("**ATLAS ANATÓMICO**")
        if os.path.exists("cuerpo.png"):
            st.image("cuerpo.png", use_container_width=True)
        else:
            zona = info_act["zona_cuerpo"]
            c_cab = color_act if zona in ["cabeza", "todo"] else "#94A3B8"
            c_pul = color_act if zona in ["pulmones", "todo"] else "#94A3B8"
            c_cor = color_act if zona in ["corazon", "todo"] else "#94A3B8"
            c_abd = color_act if zona in ["abdomen", "todo"] else "#94A3B8"
            c_rin = color_act if zona in ["rinones", "todo"] else "#94A3B8"

            st.markdown(f"""
            <div class="card" style="text-align:center; padding:14px;">
                <svg viewBox="0 0 160 320" style="width:100%; max-height:310px;">
                    <!-- Silueta humana anatómica estilizada -->
                    <path d="M80,18 C93,18 102,28 102,42 C102,54 94,63 87,66 L87,74 L118,84 C126,87 130,95 132,106 L142,168 C143,175 134,178 131,171 L119,115 L114,115 L114,185 L122,295 C122,303 109,304 107,296 L94,195 L80,195 L66,195 L53,296 C51,304 38,303 38,295 L46,185 L46,115 L41,115 L29,171 C26,178 17,175 18,168 L28,106 C30,95 34,87 42,84 L73,74 L73,66 C66,63 58,54 58,42 C58,28 67,18 80,18 Z"
                          fill="#E2E8F0" stroke="#94A3B8" stroke-width="2"/>
                    <!-- Nodos de órganos interactivos -->
                    <circle cx="80" cy="38" r="8" fill="{c_cab}" opacity="0.85"/>
                    <ellipse cx="68" cy="108" rx="9" ry="14" fill="{c_pul}" opacity="0.65"/>
                    <ellipse cx="92" cy="108" rx="9" ry="14" fill="{c_pul}" opacity="0.65"/>
                    <circle cx="85" cy="112" r="7" fill="{c_cor}"/>
                    <ellipse cx="80" cy="142" rx="14" ry="9" fill="{c_abd}" opacity="0.75"/>
                    <circle cx="67" cy="158" r="5" fill="{c_rin}"/>
                    <circle cx="93" cy="158" r="5" fill="{c_rin}"/>
                </svg>
                <div style="font-size:12px; color:#64748B; margin-top:6px;">
                    Zona activa: <b style="color:{color_act};">{zona.upper()}</b><br>
                    <i>Tip: Si guardas una imagen llamada <b>cuerpo.png</b> en esta carpeta, aparecerá aquí.</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# PESTAÑA 2: VISTA CENTRALIZADA DE TODA LA TRIPULACIÓN
# ==============================================================================
with tab_central:
    st.subheader("Vista Centralizada de la Tripulación")
    st.caption("Permite que todos los astronautas y el control médico vean el estado general en tiempo real.")
    filas = []
    for astro, valores in st.session_state.lecturas.items():
        fila = {"Tripulante": astro}
        for p_nombre, val in valores.items():
            est, _ = cfg.evaluar_estado(p_nombre, val, cfg.ASTRONAUTAS[astro])
            fila[p_nombre] = f"{val} ({est})"
        filas.append(fila)
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

# ==============================================================================
# PESTAÑA 3: SIMULADOR Y BITÁCORA MANUAL (PARA METER DATOS Y PROBAR FÓRMULAS)
# ==============================================================================
with tab_simulador:
    st.subheader(f"Ingreso de Datos y Simulación para: {astro_activo}")
    col_sim1, col_sim2 = st.columns(2)

    with col_sim1:
        st.markdown("### 1. Actualizar Parámetros (Continuos o Manuales)")
        with st.form("form_datos"):
            nuevos_valores = {}
            for p_nombre, p_info in cfg.PARAMETROS.items():
                nuevos_valores[p_nombre] = st.number_input(
                    f"{p_nombre} ({p_info['unidad']})",
                    value=float(st.session_state.lecturas[astro_activo][p_nombre]),
                    step=0.1
                )
            if st.form_submit_button("💾 Guardar y Actualizar Monitor"):
                st.session_state.lecturas[astro_activo] = nuevos_valores
                st.success("Datos actualizados en la central.")
                st.rerun()

    with col_sim2:
        st.markdown("### 2. Probador de Fórmulas Matemáticas")
        st.caption("Prueba las ecuaciones definidas en `config_medica.py` antes de enviarlas al monitor.")
        rr_input = st.number_input("Intervalo R-R del ECG (segundos):", value=1.0, min_value=0.2, max_value=2.0, step=0.05)
        hr_calc = cfg.calcular_frecuencia_desde_rr(rr_input)
        st.write(f"**Frecuencia Cardíaca calculada (`60 / RR`):** `{hr_calc} bpm`")

        st.divider()
        sbp_in = st.number_input("Presión Sistólica (SBP):", value=120)
        dbp_in = st.number_input("Presión Diastólica (DBP):", value=80)
        map_calc = cfg.calcular_presion_media(sbp_in, dbp_in)
        st.write(f"**Presión Arterial Media (`MAP`):** `{map_calc} mmHg`")

# ==============================================================================
# PESTAÑA 4: FÓRMULAS E INVESTIGACIÓN
# ==============================================================================
with tab_docs:
    st.subheader("Matriz de Justificación Científica (Configurada en `config_medica.py`)")
    for p_nombre, p_info in cfg.PARAMETROS.items():
        with st.expander(f"📌 {p_nombre} ({p_info['unidad']})"):
            st.write(f"**Fórmula:** `{p_info['formula_texto']}`")
            st.write(f"**Umbral:** {p_info['umbral_texto']}")
            st.write(f"**Justificación:** {p_info['justificacion']}")