# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN CIENTÍFICA - EGLE MONITOR
# Aquí es donde ustedes meten sus fórmulas, umbrales y protocolos investigados.
# ==============================================================================

# 1. PERFILES DE ASTRONAUTAS (Líneas base individuales)
# Agreguen o modifiquen los astronautas que quieran monitorear en la central.
ASTRONAUTAS = {
    "Astronauta 1 (Nombre / Rol)": {
        "fc_base": 60,          # <-- AQUÍ VA su frecuencia cardíaca base en reposo (bpm)
        "sistolica_base": 115,  # <-- AQUÍ VA su presión sistólica base (mmHg)
        "linfocitos_base": 2000 # <-- AQUÍ VA su conteo base de linfocitos
    },
    "Astronauta 2 (Nombre / Rol)": {
        "fc_base": 65,
        "sistolica_base": 120,
        "linfocitos_base": 1950
    },
}

# 2. CAPAS DE ENTORNO (Pueden cambiar los nombres si prefieren todo en español)
CAPAS = ["Cuerpo Humano (HB)", "Cabina (Ambient)", "Exterior / Caminata (External)"]

# 3. PARÁMETROS, FÓRMULAS Y UMBRALES
# Rellenen cada parámetro con lo que investigaron en el PDF.
PARAMETROS = {
    "Frecuencia Cardíaca": {
        "unidad": "bpm",
        "zona_cuerpo": "corazon",  # Opciones: cabeza, corazon, pulmones, abdomen, rinones, todo
        "valor_inicial": 0.0,      # <-- AQUÍ VA el dato inicial o simulado
        "formula_texto": "AQUÍ VA LA FÓRMULA (Ej: HR = 60 / Intervalo R-R)",
        "umbral_texto": "AQUÍ VA EL UMBRAL NASA (Ej: Alerta si > 100 bpm en reposo)",
        "justificacion": "AQUÍ VA POR QUÉ IMPORTA EN EL ESPACIO (Copien de su Word/PDF)",
        "protocolo": [
            "Paso 1: Escribir aquí la primera acción...",
            "Paso 2: Escribir aquí la segunda acción...",
            "Paso 3: Escribir aquí la tercera acción..."
        ],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES PREVENTIVAS PARA LA TRIPULACIÓN."
    },
    "Presión Arterial": {
        "unidad": "mmHg",
        "zona_cuerpo": "corazon",
        "valor_inicial": 0.0,
        "formula_texto": "MAP = DBP + (SBP - DBP) / 3",
        "umbral_texto": "AQUÍ VA EL UMBRAL NASA",
        "justificacion": "AQUÍ VA LA JUSTIFICACIÓN",
        "protocolo": ["Paso 1...", "Paso 2..."],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES."
    },
    "Glucosa (CGM)": {
        "unidad": "mg/dL",
        "zona_cuerpo": "abdomen",
        "valor_inicial": 0.0,
        "formula_texto": "AQUÍ VA LA FÓRMULA O TASA DE CAMBIO",
        "umbral_texto": "AQUÍ VA EL UMBRAL NASA",
        "justificacion": "AQUÍ VA LA JUSTIFICACIÓN DEL SENSOR CGM",
        "protocolo": ["Paso 1...", "Paso 2..."],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES."
    },
    "Oxigenación (SpO2)": {
        "unidad": "%",
        "zona_cuerpo": "pulmones",
        "valor_inicial": 0.0,
        "formula_texto": "AQUÍ VA LA FÓRMULA / PRESIÓN PARCIAL O2",
        "umbral_texto": "AQUÍ VA EL UMBRAL DE HIPOXIA",
        "justificacion": "AQUÍ VA LA JUSTIFICACIÓN",
        "protocolo": ["Paso 1...", "Paso 2..."],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES."
    },
    "Temperatura Corporal": {
        "unidad": "°C",
        "zona_cuerpo": "cabeza",
        "valor_inicial": 0.0,
        "formula_texto": "AQUÍ VA LA FÓRMULA DE TERMORREGULACIÓN",
        "umbral_texto": "AQUÍ VA EL UMBRAL NASA",
        "justificacion": "AQUÍ VA LA JUSTIFICACIÓN",
        "protocolo": ["Paso 1...", "Paso 2..."],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES."
    },
    "Densidad Ósea / Calcio Orina": {
        "unidad": "mg/dL",
        "zona_cuerpo": "rinones",
        "valor_inicial": 0.0,
        "formula_texto": "AQUÍ VA EL CÁLCULO DE EXCRECIÓN DE CALCIO",
        "umbral_texto": "AQUÍ VA EL UMBRAL DE RIESGO RENAL",
        "justificacion": "AQUÍ VA LA JUSTIFICACIÓN (Pérdida ósea 1-1.5% mensual)",
        "protocolo": ["Paso 1...", "Paso 2..."],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES."
    },
    "Radiación": {
        "unidad": "mSv/día",
        "zona_cuerpo": "todo",
        "valor_inicial": 0.0,
        "formula_texto": "H = Q(LET) * D",
        "umbral_texto": "AQUÍ VAN LOS LÍMITES POR ÓRGANO (NASA-STD-3001)",
        "justificacion": "AQUÍ VA LA JUSTIFICACIÓN (Neutrones CANS / GCR / SPE)",
        "protocolo": ["Paso 1...", "Paso 2..."],
        "recomendaciones": "AQUÍ VAN LAS RECOMENDACIONES."
    }
}

# 4. FUNCIÓN DE EVALUACIÓN (Lógica determinista hecha por ustedes)
def evaluar_estado(nombre_parametro, valor_actual, datos_astronauta):
    """
    AQUÍ PROGRAMAN SUS REGLAS IF / ELIF / ELSE.
    Debe devolver una tupla: ("ESTADO", "COLOR_HEX")
    Estados válidos: "NORMAL" (#0B6B63), "PRECAUCIÓN" (#D97706), "CRÍTICO" (#DC2626)
    """
    # Ejemplo de estructura lista para que ustedes pongan sus números:
    if valor_actual == 0.0:
        return "SIN DATOS", "#64748B"

    if nombre_parametro == "Frecuencia Cardíaca":
        # Ejemplo: if valor_actual > 120: return "CRÍTICO", "#DC2626"
        # Ejemplo: elif valor_actual > 90: return "PRECAUCIÓN", "#D97706"
        return "NORMAL", "#0B6B63"

    elif nombre_parametro == "Oxigenación (SpO2)":
        # Ejemplo: if valor_actual < 90: return "CRÍTICO", "#DC2626"
        return "NORMAL", "#0B6B63"

    # Por defecto si no entra en alerta:
    return "NORMAL", "#0B6B63"

# 5. FÓRMULAS MATEMÁTICAS (Para calcular valores en vivo en la pestaña Simulador)
def calcular_presion_media(sistolica, diastolic):
    # Fórmula que ya tienen en su PDF: MAP = DBP + (SBP - DBP)/3
    return round(diastolic + (sistolica - diastolic) / 3, 2)

def calcular_frecuencia_desde_rr(intervalo_rr_segundos):
    # Fórmula que ya tienen en su PDF: HR = 60 / RR
    if intervalo_rr_segundos <= 0:
        return 0.0
    return round(60.0 / intervalo_rr_segundos, 1)