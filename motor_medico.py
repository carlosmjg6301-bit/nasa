"""Motor médico determinista para la simulación de la misión EGLE.

Las reglas son una capa educativa de apoyo para la interfaz, no sustituyen
los procedimientos médicos, límites operacionales ni la autorización de vuelo.
Los nombres de sensores siguen los instrumentos y conceptos indicados para la
simulación; deben verificarse contra la configuración real de la misión.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


NOMINAL = "NOMINAL"
PRECAUCION = "PRECAUCIÓN"
CRITICO = "CRÍTICO"

ESTADOS = (NOMINAL, PRECAUCION, CRITICO)
LIMITES_DOSIS_30_DIAS_MGY_EQ = {
    "hematopoyetico_circulatorio": 250.0,
    "snc": 500.0,
    "cristalino": 1000.0,
}

Formula = dict[str, Any]
Evaluador = Callable[..., str]


def _estado_por_intervalos(
    valor: float,
    nominal: tuple[float, float],
    precaucion: tuple[float, float],
) -> str:
    if nominal[0] <= valor <= nominal[1]:
        return NOMINAL
    if precaucion[0] <= valor <= precaucion[1]:
        return PRECAUCION
    return CRITICO


def _estado_por_desviacion(
    valor: float, linea_base: float, precaucion: float = 0.2, critico: float = 0.3
) -> str:
    if linea_base <= 0:
        raise ValueError("La línea base debe ser mayor que cero")
    desviacion = abs(valor - linea_base) / linea_base
    if desviacion <= precaucion:
        return NOMINAL
    if desviacion <= critico:
        return PRECAUCION
    return CRITICO


def calcular_hr(rr_interval_sec: float) -> float:
    if rr_interval_sec <= 0:
        raise ValueError("El intervalo RR debe ser mayor que cero")
    return 60.0 / rr_interval_sec


def calcular_map(sbp: float, dbp: float) -> float:
    return dbp + (sbp - dbp) / 3.0


def calcular_caida_porcentual(valor: float, linea_base: float) -> float:
    if linea_base <= 0:
        raise ValueError("La línea base debe ser mayor que cero")
    return (linea_base - valor) / linea_base * 100.0


def calcular_dosis_equivalente_efectiva(q_let: float, dosis_absorbida: float) -> float:
    if q_let < 0 or dosis_absorbida < 0:
        raise ValueError("Q(LET) y la dosis absorbida no pueden ser negativas")
    return q_let * dosis_absorbida


def evaluar_frecuencia_cardiaca(
    heart_rate: float, fc_reposo: float | None = None
) -> str:
    estado = _estado_por_intervalos(heart_rate, (50.0, 100.0), (40.0, 120.0))
    if fc_reposo is not None:
        estado_base = _estado_por_desviacion(heart_rate, fc_reposo)
        if estado_base == CRITICO:
            return CRITICO
        if estado_base == PRECAUCION and estado == NOMINAL:
            return PRECAUCION
    return estado


def evaluar_presion_arterial(sbp: float, dbp: float) -> str:
    if sbp <= 0 or dbp <= 0:
        raise ValueError("La presión arterial debe ser mayor que cero")
    if sbp < 90 or sbp > 160 or dbp < 60 or dbp > 100:
        return CRITICO
    if sbp > 130 or dbp > 85:
        return PRECAUCION
    return NOMINAL


def evaluar_glucosa(glucose_cgm: float) -> str:
    return _estado_por_intervalos(glucose_cgm, (70.0, 140.0), (54.0, 180.0))


def evaluar_spo2(spo2: float) -> str:
    if spo2 < 90:
        return CRITICO
    if spo2 < 94:
        return PRECAUCION
    return NOMINAL


def evaluar_temperatura(body_temp: float) -> str:
    return _estado_por_intervalos(body_temp, (36.0, 38.0), (35.0, 39.0))


def evaluar_sueno_fatiga(sleep_hours: float, noches_bajas: int = 1) -> str:
    if sleep_hours < 4.0 or noches_bajas >= 3 and sleep_hours <= 6.0:
        return CRITICO
    if sleep_hours <= 6.0:
        return PRECAUCION
    return NOMINAL


def evaluar_calcio_urinario(urinary_calcium_mg_dl: float) -> str:
    if urinary_calcium_mg_dl < 0:
        raise ValueError("El calcio urinario no puede ser negativo")
    if urinary_calcium_mg_dl > 15.0:
        return CRITICO
    if urinary_calcium_mg_dl > 10.0:
        return PRECAUCION
    return NOMINAL


def evaluar_radiacion(
    rad_ambient_msv: float,
    rad_external_msv: float,
    dosis_acumulada_mgy_eq: float = 0.0,
    organo: str = "hematopoyetico_circulatorio",
) -> str:
    if rad_ambient_msv < 0 or rad_external_msv < 0 or dosis_acumulada_mgy_eq < 0:
        raise ValueError("Las dosis y tasas de dosis no pueden ser negativas")
    if organo not in LIMITES_DOSIS_30_DIAS_MGY_EQ:
        raise ValueError(f"Órgano no reconocido: {organo}")

    limite = LIMITES_DOSIS_30_DIAS_MGY_EQ[organo]
    if rad_external_msv > 3.0 or dosis_acumulada_mgy_eq >= limite:
        return CRITICO
    if rad_external_msv > 1.5 or dosis_acumulada_mgy_eq >= limite * 0.8:
        return PRECAUCION
    return NOMINAL


MEDIDAS_MEDICAS: dict[str, dict[str, Any]] = {
    "frecuencia_cardiaca": {
        "medida": {
            "nombre": "Frecuencia cardíaca",
            "unidad": "lpm",
            "sensor": "PPG/ECG AstroSkin",
        },
        "formula": {
            "ecuacion": "HR = 60 / RR_interval",
            "calculo": calcular_hr,
        },
        "umbral_espacial": evaluar_frecuencia_cardiaca,
        "protocolo": [
            "Detener la actividad y sentarse o asegurarse en la estación.",
            "Repetir la lectura con ECG/PPG y comparar con la línea base personal.",
            "Avisar al control de misión si persiste en ámbar o aparece dolor torácico, mareo o síncope.",
        ],
    },
    "presion_arterial": {
        "medida": {
            "nombre": "Presión arterial",
            "unidad": "mmHg",
            "sensor": "CBPD (Continuous Blood Pressure Device)",
        },
        "formula": {
            "ecuacion": "MAP = DBP + (SBP - DBP) / 3",
            "calculo": calcular_map,
        },
        "umbral_espacial": evaluar_presion_arterial,
        "protocolo": [
            "Adoptar reposo y mantener el cuerpo asegurado.",
            "Repetir SBP/DBP tras cinco minutos y comprobar el brazalete.",
            "Informar al control de misión si se mantiene fuera de rango o hay síntomas.",
        ],
    },
    "glucosa_cgm": {
        "medida": {
            "nombre": "Glucosa CGM",
            "unidad": "mg/dL",
            "sensor": "CGM subcutáneo",
        },
        "formula": {
            "ecuacion": "tendencia = (glucosa_actual - glucosa_anterior) / intervalo_min",
            "calculo": lambda actual, anterior, intervalo_min: (actual - anterior) / intervalo_min,
        },
        "umbral_espacial": evaluar_glucosa,
        "protocolo": [
            "Suspender ejercicio y confirmar la lectura con el procedimiento disponible.",
            "Ante hipoglucemia, consumir la ración de carbohidrato autorizada y volver a medir.",
            "Ante hiperglucemia persistente, hidratarse y notificar al control de misión.",
        ],
    },
    "spo2": {
        "medida": {
            "nombre": "Saturación periférica de oxígeno",
            "unidad": "%",
            "sensor": "Oxímetro de pulso EVA",
        },
        "formula": {
            "ecuacion": "SpO2 = (HbO2 / (HbO2 + Hb)) * 100",
            "calculo": lambda hbo2, hb: hbo2 / (hbo2 + hb) * 100,
        },
        "umbral_espacial": evaluar_spo2,
        "protocolo": [
            "Abortar la EVA o detener la actividad y asegurar el cordón de seguridad.",
            "Usar oxígeno al 100% según el procedimiento autorizado.",
            "Repetir SpO2 y avisar inmediatamente al control de misión; preparar retorno presurizado.",
        ],
    },
    "temperatura_corporal": {
        "medida": {
            "nombre": "Temperatura corporal",
            "unidad": "°C",
            "sensor": "Sensor de temperatura corporal AstroSkin",
        },
        "formula": {
            "ecuacion": "T_corporal = lectura calibrada del sensor en °C",
            "calculo": lambda lectura_calibrada: lectura_calibrada,
        },
        "umbral_espacial": evaluar_temperatura,
        "protocolo": [
            "Reducir la actividad y comprobar la interfaz de refrigeración.",
            "Repetir la medición con un sensor secundario.",
            "Informar fiebre, escalofríos o alteración persistente al control de misión.",
        ],
    },
    "sueno_fatiga": {
        "medida": {
            "nombre": "Sueño y fatiga",
            "unidad": "horas de sueño continuo",
            "sensor": "Actigrafía ARCHeR",
        },
        "formula": {
            "ecuacion": "horas_sueno = fin_sueno - inicio_sueno",
            "calculo": lambda fin_sueno, inicio_sueno: fin_sueno - inicio_sueno,
        },
        "umbral_espacial": evaluar_sueno_fatiga,
        "protocolo": [
            "Reprogramar tareas no esenciales y evitar una EVA con fatiga ámbar o roja.",
            "Aplicar el protocolo de sueño, hidratación y exposición a luz programada.",
            "Notificar tres noches consecutivas de menos de 6 horas al control de misión.",
        ],
    },
    "calcio_urinario_densidad_osea": {
        "medida": {
            "nombre": "Calcio urinario y densidad ósea",
            "unidad": "mg/dL de calcio urinario",
            "sensor": "Analizador urinario y densitometría ósea QCT",
        },
        "formula": {
            "ecuacion": "riesgo_desmineralizacion = calcio_urinario / linea_base_calcio",
            "calculo": lambda calcio_urinario, linea_base_calcio: calcio_urinario / linea_base_calcio,
        },
        "umbral_espacial": evaluar_calcio_urinario,
        "protocolo": [
            "Aumentar hidratación según el plan médico y registrar la ingesta.",
            "Cumplir el ejercicio resistivo ARED y usar brazaletes de compresión en muslos si están indicados.",
            "Reportar dolor lumbar, sangre en orina o aumento persistente de calcio al control de misión.",
        ],
    },
    "radiacion_ambiental": {
        "medida": {
            "nombre": "Radiación ambiental",
            "unidad": "mSv/día",
            "sensor": "Dosímetro de neutrones CANS / HERA",
        },
        "formula": {
            "ecuacion": "Dosis equivalente efectiva = Q(LET) * D",
            "calculo": calcular_dosis_equivalente_efectiva,
        },
        "umbral_espacial": evaluar_radiacion,
        "protocolo": [
            "Cambiar a muestreo rápido y confirmar la lectura con el dosímetro redundante.",
            "Limitar la permanencia cerca del casco y dirigirse al refugio blindado.",
            "Usar estiba de agua/polietileno como blindaje y registrar la dosis acumulada.",
        ],
    },
    "radiacion_externa": {
        "medida": {
            "nombre": "Radiación externa",
            "unidad": "mSv/día",
            "sensor": "Dosímetro de neutrones CANS / HERA",
        },
        "formula": {
            "ecuacion": "caida_porcentual = (linea_base - valor) / linea_base * 100",
            "calculo": calcular_caida_porcentual,
        },
        "umbral_espacial": evaluar_radiacion,
        "protocolo": [
            "Abortar la EVA si el flujo externo supera 1.5 mSv/día o sube rápidamente.",
            "Buscar el refugio blindado con estiba de agua/polietileno.",
            "Mantener el dosímetro activo y notificar la dosis de 30 días al control de misión.",
        ],
    },
}


def evaluar_parametro(nombre: str, *args: Any, **kwargs: Any) -> str:
    """Evalúa un parámetro por su clave pública."""
    try:
        definicion = MEDIDAS_MEDICAS[nombre]
    except KeyError as exc:
        raise KeyError(f"Parámetro médico no definido: {nombre}") from exc
    return definicion["umbral_espacial"](*args, **kwargs)


def validar_estructura() -> None:
    """Falla explícitamente si una definición no conserva las cuatro claves."""
    claves = {"medida", "formula", "umbral_espacial", "protocolo"}
    for nombre, definicion in MEDIDAS_MEDICAS.items():
        if set(definicion) != claves:
            raise RuntimeError(f"Estructura inválida para {nombre}: {set(definicion)}")
        if not isinstance(definicion["protocolo"], list) or not 3 <= len(definicion["protocolo"]) <= 4:
            raise RuntimeError(f"Protocolo inválido para {nombre}")


validar_estructura()


if __name__ == "__main__":
    print(f"Definiciones cargadas: {len(MEDIDAS_MEDICAS)}")
