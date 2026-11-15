import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="EGLE Monitor · Central Médica Espacial",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. PALETA DE COLORES CLARA (Blanco, Azul Aeroespacial, Verde Clínico)
st.markdown("""
<style>
    .stApp { background-color: #F4F7FA; color: #1E293B; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1350px; }
    
    /* Encabezado superior */
    .top-header {
        background: linear-gradient(90deg, #0A8CF0 0%, #0284C7 100%);
        color: white; padding: 14px 24px; border-radius: 10px;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 16px; box-shadow: 0 2px 6px rgba(10, 140, 240, 0.2);
    }
    
    /* Tarjetas blancas estilo tablero */
    .panel-card {
        background-color: #FFFFFF; border: 1px solid #DCE4EC;
        border-radius: 12px; padding: 20px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        margin-bottom: 14px;
    }
    
    /* Número gigante central (Hero Readout) */
    .hero-title { font-size: 20px; font-weight: 700; color: #475569; letter-spacing: 0.05em; text-transform: uppercase; }
    .hero-number { font-size: 76px; font-weight: 800; line-height: 1.05; margin: 8px 0; }
    .hero-unit { font-size: 26px; font-weight: 600; color: #64748B; }
    
    /* Etiquetas de estado */
    .badge { padding: 5px 14px; border-radius: 999px; font-size: 13px; font-weight: 700; display: inline-block; }
    .badge-normal { background-color: #DCFCE7; color: #0B6B63; border: 1px solid #86EFAC; }
    .badge-precaucion { background-color: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; }
    .badge-critico { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
    
    /* Botones de la barra izquierda */
    div.stButton > button {
        width: 100%; text-align: left; justify-content: flex-start;
        background-color: #FFFFFF; color: #1E293B; border: 1px solid #CBD5E1;
        border-radius: 10px; padding: 14px 16px; font-weight: 600;
        transition: all 0.15s ease;
    }
    div.stButton > button:hover {
        border-color: #0A8CF0; background-color: #F0F9FF; color: #0A8CF0;
    }
</style>
""", unsafe_allow_html=True)

# 3. BASE DE DATOS SIMULADA POR PERFIL Y CAPA (HB, AMBIENT, EXTERNAL)
PERFILES = {
    "Comandante (Estado Nominal)": {
        "HB": {
            "Radiation": {
                "valor": "0.42", "unidad": "mSv/día", "estado": "NORMAL",
                "organo": "cuerpo",
                "formula": "H = Q(LET) × D | Dosis acumulada: 78 / 600 mSv (Límite carrera NASA)",
                "umbral": "Alerta si dosis supera 250 mGy-Eq en 30 días (Órganos hematopoyéticos).",
                "justificacion": "Mide la radiación ionizante absorbida por el tripulante mediante dosímetro personal activo (CAD/HERA).",
                "protocolo": [
                    "1. Verificar sincronización del dosímetro personal con la telemetría local.",
                    "2. Comparar dosis superficial en piel contra dosis profunda en tejidos.",
                    "3. Registrar exposición acumulada en la bitácora offline."
                ],
                "recomendaciones": "Mantener rotación normal de estaciones. Blindaje interior de cabina operando dentro de parámetros seguros."
            },
            "Heart Rate": {
                "valor": "60", "unidad": "bpm", "estado": "NORMAL",
                "organo": "corazon",
                "formula": "HR = 60 / Intervalo R-R (1.00 s) | Línea base personal: 62 bpm",
                "umbral": "Alerta en reposo si HR > 90 bpm o < 45 bpm (Desacondicionamiento / Estrés).",
                "justificacion": "Monitorizado vía ECG/PPG (AstroSkin). En microgravedad el corazón reduce su volumen sistólico y requiere vigilancia constante.",
                "protocolo": [
                    "1. Confirmar estabilidad de onda ECG y contacto del sensor wearable.",
                    "2. Comparar pulso en reposo contra línea base previa al vuelo.",
                    "3. Evaluar tolerancia ortostática antes de ejercicio resistivo."
                ],
                "recomendaciones": "Ritmo cardiovascular óptimo. Continuar con la sesión programada de 45 min en equipo de resistencia ARED."
            },
            "Blood Sugar": {
                "valor": "100", "unidad": "mg/dL", "estado": "NORMAL",
                "organo": "abdomen",
                "formula": "Glucosa intersticial CGM (tiempo real) | Tendencia: Estable (+2 mg/dL)",
                "umbral": "Precaución si < 70 mg/dL (Hipoglucemia) o > 140 mg/dL sostenido.",
                "justificacion": "Medido con Monitor Continuo de Glucosa (CGM) subcutáneo para evitar gotas de sangre flotantes en gravedad cero y vigilar resistencia a la insulina espacial.",
                "protocolo": [
                    "1. Validar calibración del parche CGM vía Bluetooth local.",
                    "2. Correlacionar lectura con la última ingesta calórica.",
                    "3. Verificar estado de hidratación del tripulante."
                ],
                "recomendaciones": "Nivel glucémico ideal. Mantener ración balanceada de carbohidratos complejos y consumir 500 mL de electrolitos."
            },
            "SpO2": {
                "valor": "98", "unidad": "%", "estado": "NORMAL",
                "organo": "pulmones",
                "formula": "Saturación periférica O2 | Presión parcial cabina: 21.3 kPa",
                "umbral": "Precaución si SpO2 < 94% | Crítico si SpO2 < 90% (Riesgo de Hipoxia).",
                "justificacion": "Evalúa el intercambio gaseoso pulmonar y detecta fallas silenciosas en los generadores de oxígeno de la nave o traje espacial.",
                "protocolo": [
                    "1. Verificar lectura del oxímetro de pulso en dedo o lóbulo.",
                    "2. Cruzar dato con sensores ambientales de O2 y CO2 en cabina.",
                    "3. Confirmar ausencia de mareo o fatiga."
                ],
                "recomendaciones": "Oxigenación arterial completa. No se requieren ajustes en el sistema de soporte vital."
            },
            "Body Temp": {
                "valor": "36.8", "unidad": "°C", "estado": "NORMAL",
                "organo": "cabeza",
                "formula": "Temp. Central Estimada = T_piel + α(T_piel - T_cabina) | Cabina: 22.5 °C",
                "umbral": "Precaución si > 37.8 °C (Fiebre/Infección) o < 35.5 °C (Hipotermia).",
                "justificacion": "En microgravedad no existe convección natural del aire, lo que dificulta disipar el calor corporal y altera la termorregulación.",
                "protocolo": [
                    "1. Leer flujo térmico continuo del sensor portátil.",
                    "2. Verificar flujo de ventilación en el módulo actual.",
                    "3. Descartar reactivación viral por estrés de aislamiento."
                ],
                "recomendaciones": "Termorregulación estable. Mantener ventiladores de circulación de aire en velocidad nominal."
            },
            "Sleep & Bone": {
                "valor": "7.5", "unidad": "h / noche", "estado": "NORMAL",
                "organo": "rinones",
                "formula": "Actigrafía ARCHeR (7 días) | Calcio urinario manual: 180 mg/24h",
                "umbral": "Alerta cognitiva si sueño ≤ 6.0 h por 3 noches | Calcio urinario > 250 mg/24h.",
                "justificacion": "El desajuste circadiano (16 amaneceres/día) causa fatiga crítica, y la ingravidez desmineraliza 1.5% del hueso al mes elevando riesgo de cálculos renales.",
                "protocolo": [
                    "1. Revisar registro nocturno de movimiento y luz ambiental (ARCHeR).",
                    "2. Ingresar muestra periódica de calcio urinario en bitácora clínica.",
                    "3. Ajustar iluminación LED de cabina según ciclo circadiano."
                ],
                "recomendaciones": "Descanso reparador y excreción de calcio controlada. Mantener protocolo de hidratación de 2.5 L/día."
            }
        }
    },
    "Especialista EVA (Alerta Hipoxia y Radiación)": {
        "HB": {
            "Radiation": {
                "valor": "1.95", "unidad": "mSv/día", "estado": "CRÍTICO",
                "organo": "cuerpo",
                "formula": "H = Q(LET) × D | Pico de flujo detectado (Anomalía Atlántico Sur / Tormenta)",
                "umbral": "CRÍTICO: Flujo exterior > 1.50 mSv/día sin blindaje de casco.",
                "justificacion": "Exposición elevada a protones y neutrones secundarios (CANS) aumenta el riesgo agudo en médula ósea y cristalino.",
                "protocolo": [
                    "1. ABORTAR caminata espacial (EVA) inmediatamente y regresar a esclusa.",
                    "2. Activar modo de muestreo rápido cada 20 segundos.",
                    "3. Trasladar tripulación al refugio blindado con paredes de agua/polietileno."
                ],
                "recomendaciones": "EMERGENCIA DE RADIACIÓN: Permanecer en zona blindada hasta que el flujo exterior descienda por debajo de 0.80 mSv/día."
            },
            "Heart Rate": {
                "valor": "138", "unidad": "bpm", "estado": "PRECAUCIÓN",
                "organo": "corazon",
                "formula": "HR = 60 / Intervalo R-R (0.43 s) | +76 bpm sobre línea base",
                "umbral": "Precaución en EVA > 130 bpm sostenido | Crítico > 155 bpm.",
                "justificacion": "Indica alto gasto metabólico y sobrecarga térmica dentro del traje presurizado.",
                "protocolo": [
                    "1. Detener maniobras físicas de alto torque en el exterior.",
                    "2. Anclar línea de seguridad y mantener reposo por 5 minutos.",
                    "3. Aumentar flujo de enfriamiento líquido (LCG) del traje."
                ],
                "recomendaciones": "Sobreesfuerzo cardiovascular detectado. Pausar actividad física y monitorear descenso de pulso cada 2 minutos."
            },
            "Blood Sugar": {
                "valor": "115", "unidad": "mg/dL", "estado": "NORMAL",
                "organo": "abdomen",
                "formula": "Glucosa CGM: 115 mg/dL (Respuesta glucogénica por estrés EVA)",
                "umbral": "Alerta si < 70 mg/dL o > 140 mg/dL.",
                "justificacion": "El estrés físico eleva ligeramente la glucosa disponible para demanda muscular.",
                "protocolo": [
                    "1. Mantener monitoreo continuo vía telemetría del traje.",
                    "2. Verificar reserva en bolsa de hidratación interna (IDB)."
                ],
                "recomendaciones": "Reservas energéticas adecuadas. Dar sorbos cortos de agua con electrolitos."
            },
            "SpO2": {
                "valor": "89", "unidad": "%", "estado": "CRÍTICO",
                "organo": "pulmones",
                "formula": "SpO2: 89% | Caída de presión en circuito O2 del traje (< 29.6 kPa)",
                "umbral": "CRÍTICO: SpO2 < 90% requiere intervención inmediata por hipoxia.",
                "justificacion": "La hipoxia en espacio vacío provoca pérdida de conciencia en menos de 15 segundos si no se presuriza.",
                "protocolo": [
                    "1. ACTIVAR válvula de suministro de oxígeno secundario (SOP) al 100%.",
                    "2. Verificar sellado de visor y presión interna del traje.",
                    "3. Iniciar retorno asistido inmediato a la esclusa de aire con apoyo de compañero."
                ],
                "recomendaciones": "ALERTA ROJA DE HIPOXIA: El compañero de tripulación debe asistir el ingreso a cabina y preparar mascarilla de O2 puro."
            },
            "Body Temp": {
                "valor": "37.9", "unidad": "°C", "estado": "PRECAUCIÓN",
                "organo": "cabeza",
                "formula": "Temp. Central: 37.9 °C (+1.1 °C sobre línea base)",
                "umbral": "Precaución > 37.8 °C (Estrés térmico en traje EVA).",
                "justificacion": "Acumulación de calor metabólico por falla en disipación térmica del traje.",
                "protocolo": [
                    "1. Subir al máximo el flujo de la prenda de enfriamiento líquido (LCG).",
                    "2. Buscar sombra estructural de la nave durante pase orbital."
                ],
                "recomendaciones": "Riesgo de golpe de calor en traje. Reducir carga de trabajo y rehidratar al ingresar a cabina."
            },
            "Sleep & Bone": {
                "valor": "5.2", "unidad": "h / noche", "estado": "PRECAUCIÓN",
                "organo": "rinones",
                "formula": "Sueño: 5.2 h (3 noches seguidas < 6 h) | Calcio urinario: 275 mg/24h",
                "umbral": "Precaución: Déficit acumulado de sueño + hipercalciuria.",
                "justificacion": "La fatiga reduce la velocidad de reacción en emergencias y la deshidratación en EVA eleva el riesgo de litiasis renal.",
                "protocolo": [
                    "1. Restringir tareas críticas de precisión tras finalizar la EVA.",
                    "2. Administrar protocolo de rehidratación intensiva con citrato de potasio."
                ],
                "recomendaciones": "Asignar periodo obligatorio de descanso de 8.5 h y terapia de luz azul/ámbar para reajustar ritmo circadiano."
            }
        }
    }
}

# Datos compartidos para las pestañas AMBIENT y EXTERNAL
CAPAS_ENTORNO = {
    "AMBIENT": {
        "Radiation": {"valor": "0.38", "unidad": "mSv/día", "estado": "NORMAL", "organo": "cuerpo", "formula": "Neutrones internos CANS: 0.8 part/(s·cm²)", "umbral": "Alerta cabina > 0.80 mSv/día", "justificacion": "Los neutrones secundarios representan ~30% de la dosis dentro de la nave.", "protocolo": ["1. Monitorear espectrómetro CANS en módulo habitable.", "2. Verificar integridad de estiba de agua."], "recomendaciones": "Atenuación del casco nominal. Ambiente interior seguro."},
        "Heart Rate": {"valor": "64", "unidad": "bpm (Promedio)", "estado": "NORMAL", "organo": "corazon", "formula": "Promedio biométrico de tripulación en cabina", "umbral": "Alerta grupal > 95 bpm", "justificacion": "Evalúa carga de trabajo colectiva y estrés ambiental en el hábitat.", "protocolo": ["1. Cruzar pulso grupal con niveles de CO2 en cabina."], "recomendaciones": "Carga fisiológica de la tripulación estable."},
        "Blood Sugar": {"valor": "98", "unidad": "mg/dL (Media)", "estado": "NORMAL", "organo": "abdomen", "formula": "Índice glucémico post-ingesta de tripulación", "umbral": "Rango nominal 70 - 140 mg/dL", "justificacion": "Verifica calidad nutricional y estabilidad energética a bordo.", "protocolo": ["1. Registrar cumplimiento de dieta espacial."], "recomendaciones": "Estabilidad metabólica grupal confirmada."},
        "SpO2": {"valor": "20.9", "unidad": "% O2 Cabina", "estado": "NORMAL", "organo": "pulmones", "formula": "Presión total: 101.3 kPa | ppCO2: 2.8 mmHg", "umbral": "Alerta si O2 < 19.5% o ppCO2 > 4.0 mmHg", "justificacion": "Control atmosférico cerrado para evitar hipercapnia e hipoxia.", "protocolo": ["1. Verificar regeneración de filtros CDRA de CO2."], "recomendaciones": "Atmósfera de cabina equilibrada y respirable."},
        "Body Temp": {"valor": "22.5", "unidad": "°C Cabina", "estado": "NORMAL", "organo": "cabeza", "formula": "Humedad relativa: 45% RH | Flujo aire: Nominal", "umbral": "Rango confort NASA: 18 °C - 27 °C", "justificacion": "Evita condensación en paneles eléctricos y mantiene confort térmico.", "protocolo": ["1. Revisar intercambiadores de calor de aviónica."], "recomendaciones": "Temperatura ambiental óptima."},
        "Sleep & Bone": {"valor": "LED", "unidad": "Modo Día", "estado": "NORMAL", "organo": "rinones", "formula": "Iluminación de estado sólido (SSLA) 480 nm", "umbral": "Cambio a espectro cálido 2 h antes de dormir", "justificacion": "La luz azul controlada regula la melatonina ante 16 amaneceres orbitales.", "protocolo": ["1. Sincronizar luces LED con horario fijo de sueño."], "recomendaciones": "Ciclo lumínico sincronizado con horario de misión."}
    },
    "EXTERNAL": {
        "Radiation": {"valor": "1.85", "unidad": "mSv/día", "estado": "CRÍTICO", "organo": "cuerpo", "formula": "Flujo exterior sin blindaje (Detector HERA Ext)", "umbral": "Alerta EVA si flujo > 1.50 mSv/día", "justificacion": "Mide rayos cósmicos galácticos y partículas solares fuera del casco.", "protocolo": ["1. Evaluar ventana orbital antes de abrir escotilla.", "2. Cancelar actividades extravehiculares si sube el flujo."], "recomendaciones": "Flujo exterior elevado por cruce orbital. Mantener escotillas cerradas."},
        "Heart Rate": {"valor": "112", "unidad": "bpm (Traje)", "estado": "NORMAL", "organo": "corazon", "formula": "Telemetría biométrica de arnés EVA", "umbral": "Límite operativo EVA: 150 bpm", "justificacion": "Estima gasto energético y producción de calor dentro del traje.", "protocolo": ["1. Monitorear consumo de O2 proporcional al pulso."], "recomendaciones": "Esfuerzo moderado acorde a traslación exterior."},
        "Blood Sugar": {"valor": "108", "unidad": "mg/dL (EVA)", "estado": "NORMAL", "organo": "abdomen", "formula": "CGM transmitido por bus de traje espacial", "umbral": "Alerta < 75 mg/dL durante caminata", "justificacion": "Previene fatiga o mareo durante maniobras fuera de la nave.", "protocolo": ["1. Recordar ingesta de bebida isotónica en casco."], "recomendaciones": "Nivel energético estable para completar tarea."},
        "SpO2": {"valor": "29.6", "unidad": "kPa Traje", "estado": "NORMAL", "organo": "pulmones", "formula": "100% Oxígeno puro (4.3 psi) | Canister LiOH OK", "umbral": "Alerta crítica si presión cae < 26.0 kPa", "justificacion": "Presurización crítica para evitar enfermedad por descompresión.", "protocolo": ["1. Verificar regulador primario de oxígeno del traje."], "recomendaciones": "Presión de traje nominal y sin fugas."},
        "Body Temp": {"valor": "-110/+115", "unidad": "°C Exterior", "estado": "NORMAL", "organo": "cabeza", "formula": "Gradiente térmico orbital día/noche", "umbral": "Mantener núcleo humano entre 36.5 °C y 37.8 °C", "justificacion": "El vacío espacial genera extremos térmicos severos cada 45 minutos.", "protocolo": ["1. Regular sublimador de enfriamiento en fase solar.", "2. Activar calentadores de guantes en eclipse."], "recomendaciones": "Aislamiento multicapa (MLI) operando correctamente."},
        "Sleep & Bone": {"valor": "0.00", "unidad": "g (Vacío)", "estado": "PRECAUCIÓN", "organo": "rinones", "formula": "Microgravedad extrema fuera de estación", "umbral": "Máximo 6.5 h continuas de operación EVA", "justificacion": "La fatiga muscular en manos y antebrazos aumenta el riesgo de error operativo.", "protocolo": ["1. Programar pausas de descanso de 5 min cada hora."], "recomendaciones": "Evitar fatiga de agarre en herramientas."}
    }
}

# Inicializar estado de selección
if "param_activo" not in st.session_state:
    st.session_state.param_activo = "Heart Rate"
if "capa_activa" not in st.session_state:
    st.session_state.capa_activa = "HB"

# 4. ENCABEZADO SUPERIOR Y SELECTORES DE CENTRAL
st.markdown("""
<div class="top-header">
    <div>
        <span style="font-size:20px; font-weight:800; letter-spacing:0.04em;">EGLE MONITOR</span>
        <span style="font-size:13px; opacity:0.9; margin-left:12px;">Central Autónoma de Salud · Misión Día 142</span>
    </div>
    <div style="font-size:12px; font-weight:600; background:rgba(255,255,255,0.2); padding:5px 12px; border-radius:999px;">
        🟢 SQLite Offline · Integridad Anti-SEU OK
    </div>
</div>
""", unsafe_allow_html=True)

# Barra de control: Selección de Astronauta + Selector de Capa (HB | AMBIENT | EXTERNAL)
col_perfil, col_capas = st.columns([1.2, 2])
with col_perfil:
    perfil = st.selectbox("👨‍🚀 Tripulante monitoreado (Central):", list(PERFILES.keys()), label_visibility="collapsed")
with col_capas:
    capa = st.radio(
        "Capa de telemetría:",
        ["HB", "AMBIENT", "EXTERNAL"],
        format_func=lambda x: {"HB": "🧍 HB (Cuerpo Humano)", "AMBIENT": "🛸 AMBIENT (Cabina)", "EXTERNAL": "🌌 EXTERNAL (Espacio / EVA)"}[x],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.capa_activa = capa

# Obtener datos según perfil y capa
datos_actuales = PERFILES[perfil]["HB"] if capa == "HB" else CAPAS_ENTORNO[capa]
activo = datos_actuales[st.session_state.param_activo]

# Determinar colores según estado
color_hex = {"NORMAL": "#0B6B63", "PRECAUCIÓN": "#D97706", "CRÍTICO": "#DC2626"}[activo["estado"]]
badge_css = {"NORMAL": "badge-normal", "PRECAUCIÓN": "badge-precaucion", "CRÍTICO": "badge-critico"}[activo["estado"]]

# 5. ESTRUCTURA DEL PIZARRÓN: IZQUIERDA (Botones) | DERECHA (Protocolo + Número Gigante + Recomendaciones)
col_izq, col_der = st.columns([1, 2.7], gap="medium")

with col_izq:
    st.markdown("<div style='font-size:12px; font-weight:700; color:#64748B; margin-bottom:8px; letter-spacing:0.05em;'>PARÁMETROS EN VIVO</div>", unsafe_allow_html=True)
    for nombre_param, info in datos_actuales.items():
        icono_estado = {"NORMAL": "🟢", "PRECAUCIÓN": "🟡", "CRÍTICO": "🔴"}[info["estado"]]
        etiqueta = f"{icono_estado}  {nombre_param}  —  {info['valor']} {info['unidad']}"
        if st.button(etiqueta, key=f"btn_{nombre_param}"):
            st.session_state.param_activo = nombre_param
            st.rerun()

with col_der:
    # Mitad superior: Protocolo (Izquierda) + Valor Gigante (Derecha)
    sub_prot, sub_valor = st.columns([1.1, 1], gap="medium")
    
    with sub_prot:
        pasos_html = "".join([f"<p style='margin:8px 0; font-size:14px; color:#334155;'>{p}</p>" for p in activo["protocolo"]])
        # Esquema SVG del astronauta iluminando el órgano afectado
        c_cabeza = color_hex if activo["organo"] == "cabeza" else "#CBD5E1"
        c_corazon = color_hex if activo["organo"] in ["corazon", "pulmones"] else "#CBD5E1"
        c_abdomen = color_hex if activo["organo"] in ["abdomen", "rinones"] else "#CBD5E1"
        c_cuerpo = color_hex if activo["organo"] == "cuerpo" else "#94A3B8"
        
        svg_cuerpo = f"""
        <svg width="75" height="95" viewBox="0 0 80 100" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:4px;">
            <circle cx="40" cy="18" r="11" fill="{c_cabeza}" stroke="{c_cuerpo}" stroke-width="2"/>
            <rect x="26" y="33" width="28" height="34" rx="6" fill="#E2E8F0" stroke="{c_cuerpo}" stroke-width="2"/>
            <circle cx="44" cy="43" r="5" fill="{c_corazon}"/>
            <circle cx="36" cy="56" r="5" fill="{c_abdomen}"/>
            <line x1="26" y1="38" x2="14" y2="60" stroke="{c_cuerpo}" stroke-width="4" stroke-linecap="round"/>
            <line x1="54" y1="38" x2="66" y2="60" stroke="{c_cuerpo}" stroke-width="4" stroke-linecap="round"/>
            <line x1="33" y1="67" x2="30" y2="92" stroke="{c_cuerpo}" stroke-width="4" stroke-linecap="round"/>
            <line x1="47" y1="67" x2="50" y2="92" stroke="{c_cuerpo}" stroke-width="4" stroke-linecap="round"/>
        </svg>
        """
        
        st.markdown(f"""
        <div class="panel-card" style="min-height: 290px; border-top: 4px solid {color_hex};">
            <div style="font-size:17px; font-weight:800; color:#0F172A; margin-bottom:10px;">📋 Protocolo de Acción</div>
            {pasos_html}
            <div style="display:flex; align-items:center; gap:14px; margin-top:14px; padding-top:10px; border-top:1px solid #F1F5F9;">
                {svg_cuerpo}
                <div style="font-size:12px; color:#64748B;">
                    <b style="color:#0F172A;">Atlas Biométrico</b><br>
                    Zona monitoreada activa.<br>
                    Guía diseñada para tripulación sin formación médica.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sub_valor:
        st.markdown(f"""
        <div class="panel-card" style="min-height: 290px; text-align:center; display:flex; flex-direction:column; justify-content:center; border-top: 4px solid {color_hex};">
            <div><span class="badge {badge_css}">● {activo['estado']} · {capa}</span></div>
            <div class="hero-title" style="margin-top:14px;">{st.session_state.param_activo}</div>
            <div class="hero-number" style="color:{color_hex};">{activo['valor']}</div>
            <div class="hero-unit">{activo['unidad']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Botón de ayuda (?) para mostrar la matemática, umbral y justificación científica sin ensuciar la pantalla
    with st.expander("❓ Ver Fórmula Matemática, Umbral Espacial y Justificación Científica"):
        st.markdown(f"""
        * **📐 Fórmula / Cálculo:** `{activo['formula']}`
        * **🚨 Umbral de Alerta NASA:** {activo['umbral']}
        * **🔬 Justificación Fisiológica:** {activo['justificacion']}
        """)

    # Caja inferior: Recomendaciones (igual que en el dibujo del pizarrón)
    st.markdown(f"""
    <div class="panel-card" style="border-left: 5px solid #0A8CF0;">
        <div style="font-size:16px; font-weight:800; color:#0F172A; margin-bottom:6px;">💡 Recomendaciones Operativas</div>
        <div style="font-size:15px; color:#334155; line-height:1.5;">{activo['recomendaciones']}</div>
    </div>
    """, unsafe_allow_html=True)