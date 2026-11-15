# ==============================================================================
# CONFIGURACIÓN CIENTÍFICA OFICIAL - EGLE MONITOR (Basado en egle (1).pdf)
# ==============================================================================

# 1. PERFILES DE ASTRONAUTAS (Líneas base individuales)
ASTRONAUTAS = {
    "Comandante (Nominal)": {
        "fc_base": 62,
        "sistolica_base": 117,
        "linfocitos_base": 2000,
        "pvt_base_ms": 240,
        "poms_tmd_base": 12
    },
    "Especialista de Misión (Fatiga / Radiación)": {
        "fc_base": 65,
        "sistolica_base": 118,
        "linfocitos_base": 1950,
        "pvt_base_ms": 250,
        "poms_tmd_base": 15
    },
}

# 2. CAPAS DE ENTORNO
CAPAS = ["Cuerpo Humano (HB)", "Cabina (Ambient)", "Exterior / EVA (External)"]

# 3. PARÁMETROS, FÓRMULAS Y UMBRALES EXTRAÍDOS DE SU INVESTIGACIÓN
PARAMETROS = {
    "Radiación Personal (MDU)": {
        "unidad": "mSv/h",
        "zona_cuerpo": "todo",
        "valor_inicial": 0.03,
        "formula_texto": "H (mSv) = [Absorbed Dose Rate (uGy/h) * Time (h) / 1000] * Q(LET)",
        "umbral_texto": "Nominal: 0.02-0.04 mSv/h | Precaución: >0.05 mSv/h | Crítico: >0.50 mSv/h (Límite 30d BFO: 250 mGy-Eq)",
        "justificacion": "Los dosímetros personales de silicio (MDU/Liulin) miden la dosis localizada absorbida por el astronauta (protones, GCR y neutrones secundarios detectados por CANS) con factores de calidad Q(LET).",
        "protocolo": [
            "1. Confirmar que el MDU esté colocado correctamente en el torso.",
            "2. Verificar activación de Fast Mode (muestreo cada 20 s en lugar de 90 s).",
            "3. Si cabina > 1.0 mSv/h o alerta roja: trasladar tripulación al módulo central blindado hasta bajar de 0.10 mSv/h."
        ],
        "recomendaciones": "Mantener rotación en módulos con blindaje de agua/polietileno y vigilar conteo de linfocitos a las 12-48 h ante picos."
    },
    "Frecuencia Cardíaca": {
        "unidad": "bpm",
        "zona_cuerpo": "corazon",
        "valor_inicial": 62.0,
        "formula_texto": "HR = 60 / Intervalo R-R (s) | Complementado con HRV (ms) vía ECG/PPG",
        "umbral_texto": "Reposo Nominal: 50-90 bpm | Precaución: >90 bpm | Crítico: >120 bpm en reposo (o >150 bpm en EVA)",
        "justificacion": "Monitorizado mediante sensores portátiles (AstroSkin / Equivital) para evaluar adaptación cardiovascular y estrés autonómico en microgravedad.",
        "protocolo": [
            "1. Adquirir señal ECG/PPG y verificar estabilidad del intervalo R-R.",
            "2. Comparar lectura en reposo contra la línea base personal previa al vuelo.",
            "3. Evaluar tolerancia ortostática antes de sesiones de ejercicio resistivo."
        ],
        "recomendaciones": "Continuar protocolo diario de ejercicio aeróbico y resistivo para prevenir desacondicionamiento cardíaco."
    },
    "Presión Arterial (MAP)": {
        "unidad": "mmHg",
        "zona_cuerpo": "corazon",
        "valor_inicial": 93.0,
        "formula_texto": "MAP = DBP + (SBP - DBP) / 3 (Medido vía CBPD o Pulse Transit Time)",
        "umbral_texto": "MAP Nominal: 70-100 mmHg | Precaución: >105 o <65 mmHg (Riesgo ortostático)",
        "justificacion": "Evalúa el desplazamiento cefálico de fluidos hacia la cabeza en microgravedad y el riesgo de intolerancia ortostática al cambiar de campo gravitatorio.",
        "protocolo": [
            "1. Verificar calibración del manguito digital (CBPD) o sensor PTT.",
            "2. Evaluar síntomas visuales o cefalea por presión craneal.",
            "3. Aplicar brazaletes de compresión en muslos o presión negativa inferior (LBNP) si hay congestión cefálica."
        ],
        "recomendaciones": "Mantener hidratación adecuada antes de transiciones gravitacionales."
    },
    "Glucosa (CGM)": {
        "unidad": "mg/dL",
        "zona_cuerpo": "abdomen",
        "valor_inicial": 100.0,
        "formula_texto": "Telemetría intersticial continua (CGM subcutáneo) vs. línea base glucémica",
        "umbral_texto": "Nominal: 70-140 mg/dL | Precaución: >140 mg/dL sostenido | Crítico: <70 mg/dL (Hipoglucemia)",
        "justificacion": "La atrofia muscular por desuso induce resistencia a la insulina espacial (NASA Twins Study). El CGM evita punciones capilares y gotas de sangre flotantes en 0g.",
        "protocolo": [
            "1. Validar enlace inalámbrico del sensor CGM subcutáneo.",
            "2. Correlacionar lectura con última ingesta calórica y carga de trabajo.",
            "3. Si < 70 mg/dL, administrar carbohidratos de absorción rápida inmediatamente."
        ],
        "recomendaciones": "Mantener dieta espacial balanceada y consumo regular de electrolitos."
    },
    "Oxigenación (SpO2)": {
        "unidad": "%",
        "zona_cuerpo": "pulmones",
        "valor_inicial": 98.0,
        "formula_texto": "Saturación arterial periférica (%) + Verificación ppO2 cabina (21.3 kPa) / traje (29.6 kPa)",
        "umbral_texto": "Nominal: >=95% | Precaución: 90-94% | Crítico: <90% (Hipoxia aguda)",
        "justificacion": "Detecta fallas en la presurización del traje EVA o desequilibrios en el sistema de soporte vital cerrado de la cabina.",
        "protocolo": [
            "1. Confirmar perfusión en oxímetro de pulso y cruzar con sensores de O2/CO2 de cabina.",
            "2. En EVA con SpO2 < 90%: activar oxígeno secundario (SOP) al 100% y abortar caminata hacia esclusa.",
            "3. Verificar regeneración de filtros de CO2 (CDRA) y administrar O2 suplementario."
        ],
        "recomendaciones": "Verificar sellado de escotillas y presión parcial de oxígeno antes de operaciones críticas."
    },
    "Temperatura Corporal": {
        "unidad": "°C",
        "zona_cuerpo": "cabeza",
        "valor_inicial": 37.0,
        "formula_texto": "Termometría central / flujo térmico cutáneo (Referencia clínica: >38 °C fiebre, <35 °C hipotermia)",
        "umbral_texto": "Nominal: 36.1-37.5 °C | Precaución: 37.6-38.0 °C | Crítico: >38.0 °C o <35.0 °C",
        "justificacion": "La ausencia de convección natural en microgravedad altera la disipación de calor, y el estrés inmunológico puede reactivar virus latentes.",
        "protocolo": [
            "1. Contrastar temperatura central (sensor ingerible/timpánico) contra temperatura de cabina.",
            "2. En traje EVA, regular flujo de la prenda de enfriamiento líquido (LCG).",
            "3. Aislar y realizar panel microbiano/salival si se confirma fiebre (>38 °C)."
        ],
        "recomendaciones": "Asegurar ventilación activa en módulos habitables para evitar bolsas de aire caliente."
    },
    "Sueño y Fatiga (Actigrafía)": {
        "unidad": "h/noche",
        "zona_cuerpo": "cabeza",
        "valor_inicial": 7.2,
        "formula_texto": "Eficiencia = (Tiempo dormido / Tiempo en cama)*100 | Ventana nominal: 21:30 - 06:00",
        "umbral_texto": "Normal: >=7 h (Efic >=85%) | Precaución: 6-7 h | Alerta: 5-6 h | Crítico: <5 h o PVT >500 ms",
        "justificacion": "Los 16 amaneceres orbitales diarios generan 'jet lag perpetuo'. Dormir <6 h seguidas degrada la atención sostenida y aumenta errores operativos (estudio ARCHER).",
        "protocolo": [
            "1. Revisar horas dormidas, eficiencia (<75% alerta) y despertares (WASO >30% base) en pulsera actigráfica.",
            "2. Aplicar test psicomotor PVT (alertar si aumentan lapsos >500 ms).",
            "3. Ajustar iluminación LED de estado sólido (SSLA) y restringir tareas críticas tras déficit acumulado."
        ],
        "recomendaciones": "Mantener horarios fijos de sueño/vigilia y evitar pantallas antes de dormir."
    },
    "Salud Mental y Ánimo": {
        "unidad": "pts (PHQ-9)",
        "zona_cuerpo": "cabeza",
        "valor_inicial": 2.0,
        "formula_texto": "PHQ-9 (0-27) | GAD-7 (0-21) | POMS TMD = (Ten + Dep + Ira + Fat + Conf) - Vigor",
        "umbral_texto": "Normal: 0-4 | Precaución: 5-9 | Crítico: >=10 (o cualquier respuesta >0 en Ítem 9 de PHQ-9)",
        "justificacion": "El aislamiento prolongado y el confinamiento ('tin can') alteran la regulación emocional y el volumen hipocampal (estudios Mars-500 y Antártida).",
        "protocolo": [
            "1. Evaluar cuestionarios periódicos (PHQ-9, GAD-7, POMS) y test cognitivo WinSCAT.",
            "2. Si Ítem 9 de PHQ-9 > 0: activar protocolo inmediato de apoyo psicológico y acompañamiento de tripulación.",
            "3. Monitorear frecuencia de llamadas familiares y contacto social a bordo."
        ],
        "recomendaciones": "Fomentar actividades significativas, diario personal (journaling) y contacto regular con familia."
    },
    "Densidad Ósea / Orina": {
        "unidad": "mg/24h",
        "zona_cuerpo": "rinones",
        "valor_inicial": 180.0,
        "formula_texto": "Excreción urinaria de calcio (Bitácora discreta) | Pérdida ósea esperada: 1.0-1.5% / mes",
        "umbral_texto": "Normal: <250 mg/24h | Precaución: 250-300 mg/24h | Crítico: >300 mg/24h (Riesgo nefrolitiasis)",
        "justificacion": "La descarga mecánica en 0g libera calcio óseo al torrente sanguíneo, elevando su concentración renal y el riesgo de cálculos renales.",
        "protocolo": [
            "1. Registrar periódicamente el análisis de volumen y calcio en orina en la bitácora clínica.",
            "2. Si supera 250 mg/24h: activar régimen estricto de hidratación (>2.5 L/día).",
            "3. Evaluar suplementación con citrato de potasio y cumplir rutina en equipo resistivo ARED."
        ],
        "recomendaciones": "Cumplir sesiones diarias de ejercicio de resistencia para estimular remodelación ósea."
    }
}

# 4. MOTOR DETERMINISTA DE EVALUACIÓN (Reglas exactas de su PDF)
def evaluar_estado(nombre_parametro, valor_actual, datos_astronauta):
    if valor_actual is None:
        return "SIN DATOS", "#64748B"

    if nombre_parametro == "Radiación Personal (MDU)":
        if valor_actual >= 0.50:
            return "CRÍTICO", "#DC2626"
        elif valor_actual >= 0.05:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Frecuencia Cardíaca":
        if valor_actual > 120 or valor_actual < 45:
            return "CRÍTICO", "#DC2626"
        elif valor_actual > 90:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Presión Arterial (MAP)":
        if valor_actual > 115 or valor_actual < 60:
            return "CRÍTICO", "#DC2626"
        elif valor_actual > 100 or valor_actual < 70:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Glucosa (CGM)":
        if valor_actual < 70 or valor_actual > 180:
            return "CRÍTICO", "#DC2626"
        elif valor_actual > 140:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Oxigenación (SpO2)":
        if valor_actual < 90:
            return "CRÍTICO", "#DC2626"
        elif valor_actual < 95:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Temperatura Corporal":
        if valor_actual > 38.0 or valor_actual < 35.0:
            return "CRÍTICO", "#DC2626"
        elif valor_actual > 37.5 or valor_actual < 36.0:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Sueño y Fatiga (Actigrafía)":
        if valor_actual < 5.0:
            return "CRÍTICO", "#DC2626"
        elif valor_actual < 7.0:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Salud Mental y Ánimo":
        if valor_actual >= 10:
            return "CRÍTICO", "#DC2626"
        elif valor_actual >= 5:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Densidad Ósea / Orina":
        if valor_actual > 300:
            return "CRÍTICO", "#DC2626"
        elif valor_actual >= 250:
            return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    return "NORMAL", "#0B6B63"

# 5. FÓRMULAS MATEMÁTICAS EN VIVO
def calcular_presion_media(sistolica, diastolic):
    return round(diastolic + (sistolica - diastolic) / 3, 2)

def calcular_frecuencia_desde_rr(intervalo_rr_segundos):
    if intervalo_rr_segundos <= 0:
        return 0.0
    return round(60.0 / intervalo_rr_segundos, 1)

def calcular_dosis_mdu(tasa_ugy_h, horas, factor_q_let):
    return round((tasa_ugy_h * horas / 1000.0) * factor_q_let, 4)

def calcular_tmd_poms(tension, depresion, ira, fatiga, confusion, vigor):
    return (tension + depresion + ira + fatiga + confusion) - vigor