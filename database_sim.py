"""Base de datos SQLite para simular la telemetría de la misión EGLE.

Los valores son sintéticos y sirven únicamente para pruebas de la interfaz.
"""

from __future__ import annotations

import hashlib
import json
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DB_PATH = Path(__file__).with_name("egle_mission.db")
SEED = 20261115

TRIPULACION = (
    {
        "nombre": "Comandante (Nominal)",
        "fc_reposo": 62.0,
        "presion_sistolica": 118.0,
        "linfocitos": 2010,
    },
    {
        "nombre": "Ingeniero (Fatiga/Glucosa)",
        "fc_reposo": 68.0,
        "presion_sistolica": 121.0,
        "linfocitos": 1980,
    },
    {
        "nombre": "Especialista EVA (Riesgo Hipoxia/Radiación)",
        "fc_reposo": 64.0,
        "presion_sistolica": 116.0,
        "linfocitos": 2050,
    },
)

TELEMETRIA_COLUMNAS = (
    "id_astronauta",
    "timestamp",
    "heart_rate",
    "rr_interval_sec",
    "sbp",
    "dbp",
    "glucose_cgm",
    "spo2",
    "body_temp",
    "sleep_hours",
    "rad_ambient_msv",
    "rad_external_msv",
)


def _conexion() -> sqlite3.Connection:
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def _timestamp(valor: datetime | None = None) -> str:
    momento = valor or datetime.now(timezone.utc)
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(timezone.utc).isoformat(timespec="seconds")


def _hash_telemetria(lectura: dict[str, Any]) -> str:
    valores = [lectura[columna] for columna in TELEMETRIA_COLUMNAS]
    contenido = json.dumps(valores, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def crear_esquema() -> None:
    """Crea las tablas e índices si todavía no existen."""
    with _conexion() as conexion:
        conexion.executescript(
            """
            CREATE TABLE IF NOT EXISTS tripulacion (
                id_astronauta INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                fc_reposo REAL NOT NULL,
                presion_sistolica REAL NOT NULL,
                linfocitos INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS telemetria_continua (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_astronauta INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                heart_rate REAL NOT NULL,
                rr_interval_sec REAL NOT NULL,
                sbp REAL NOT NULL,
                dbp REAL NOT NULL,
                glucose_cgm REAL NOT NULL,
                spo2 REAL NOT NULL,
                body_temp REAL NOT NULL,
                sleep_hours REAL NOT NULL,
                rad_ambient_msv REAL NOT NULL,
                rad_external_msv REAL NOT NULL,
                integrity_hash TEXT NOT NULL,
                FOREIGN KEY (id_astronauta) REFERENCES tripulacion(id_astronauta)
            );

            CREATE TABLE IF NOT EXISTS registros_discretos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_astronauta INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                urinary_calcium_mg_dl REAL NOT NULL,
                lymphocytes_count INTEGER NOT NULL,
                winscat_cognitive_score REAL NOT NULL,
                mood_status TEXT NOT NULL,
                FOREIGN KEY (id_astronauta) REFERENCES tripulacion(id_astronauta)
            );

            CREATE INDEX IF NOT EXISTS idx_telemetria_astronauta_timestamp
                ON telemetria_continua (id_astronauta, timestamp);
            CREATE INDEX IF NOT EXISTS idx_discretos_astronauta_timestamp
                ON registros_discretos (id_astronauta, timestamp);
            """
        )


def _insertar_tripulacion(conexion: sqlite3.Connection) -> dict[str, int]:
    ids: dict[str, int] = {}
    for perfil in TRIPULACION:
        conexion.execute(
            """
            INSERT OR IGNORE INTO tripulacion
                (nombre, fc_reposo, presion_sistolica, linfocitos)
            VALUES (?, ?, ?, ?)
            """,
            (
                perfil["nombre"],
                perfil["fc_reposo"],
                perfil["presion_sistolica"],
                perfil["linfocitos"],
            ),
        )
        fila = conexion.execute(
            "SELECT id_astronauta FROM tripulacion WHERE nombre = ?",
            (perfil["nombre"],),
        ).fetchone()
        if fila is None:
            raise RuntimeError(f"No se pudo registrar a {perfil['nombre']}")
        ids[perfil["nombre"]] = int(fila["id_astronauta"])
    return ids


def _generar_telemetria(
    id_astronauta: int, perfil: dict[str, Any], indice: int, momento: datetime, rng: random.Random
) -> dict[str, Any]:
    nombre = perfil["nombre"]
    es_ingeniero = "Ingeniero" in nombre
    es_eva = "Especialista" in nombre
    heart_rate = perfil["fc_reposo"] + rng.uniform(-3.0, 3.0)
    glucose = 98.0 + rng.uniform(-5.0, 5.0)
    sleep = 7.2 + rng.uniform(-0.4, 0.4)
    spo2 = 98.0 + rng.uniform(-0.8, 0.8)
    ambient = 0.50 + rng.uniform(-0.04, 0.04)
    external = 0.75 + rng.uniform(-0.10, 0.10)

    if es_ingeniero:
        sleep = 5.4 + rng.uniform(-0.5, 0.3)
        heart_rate += 5.0 + indice * 0.08
        glucose = 112.0 + indice * 0.7 + rng.uniform(-4.0, 4.0)
    elif es_eva:
        spo2 = 93.5 + rng.uniform(-1.3, 0.7)
        ambient += 0.10
        external = 1.35 + indice * 0.035 + rng.uniform(-0.12, 0.12)

    lectura = {
        "id_astronauta": id_astronauta,
        "timestamp": _timestamp(momento),
        "heart_rate": round(heart_rate, 2),
        "rr_interval_sec": round(60.0 / heart_rate, 4),
        "sbp": round(perfil["presion_sistolica"] + rng.uniform(-4.0, 4.0), 2),
        "dbp": round(76.0 + rng.uniform(-3.0, 3.0), 2),
        "glucose_cgm": round(glucose, 2),
        "spo2": round(spo2, 2),
        "body_temp": round(37.0 + rng.uniform(-0.2, 0.2), 2),
        "sleep_hours": round(sleep, 2),
        "rad_ambient_msv": round(ambient, 4),
        "rad_external_msv": round(external, 4),
    }
    lectura["integrity_hash"] = _hash_telemetria(lectura)
    return lectura


def _generar_discreto(
    id_astronauta: int, perfil: dict[str, Any], indice: int, momento: datetime, rng: random.Random
) -> tuple[Any, ...]:
    nombre = perfil["nombre"]
    if "Ingeniero" in nombre:
        calcio = 9.5 + rng.uniform(-0.4, 0.8)
        linfocitos = perfil["linfocitos"] - indice * 4 + rng.randint(-20, 20)
        winscat = 78.0 - indice * 0.4 + rng.uniform(-3.0, 3.0)
        mood = "Fatiga" if indice >= 8 else "Estable"
    elif "Especialista" in nombre:
        calcio = 10.1 + rng.uniform(-0.3, 0.8)
        linfocitos = perfil["linfocitos"] - indice * 12 + rng.randint(-25, 20)
        winscat = 84.0 + rng.uniform(-4.0, 3.0)
        mood = "Vigilancia" if indice >= 6 else "Estable"
    else:
        calcio = 9.2 + rng.uniform(-0.3, 0.3)
        linfocitos = perfil["linfocitos"] + rng.randint(-25, 25)
        winscat = 92.0 + rng.uniform(-3.0, 3.0)
        mood = "Nominal"
    return (
        id_astronauta,
        _timestamp(momento),
        round(calcio, 2),
        max(1000, int(linfocitos)),
        round(winscat, 2),
        mood,
    )


def inicializar_datos() -> None:
    """Crea la base y carga 20 lecturas de cada tipo por astronauta."""
    crear_esquema()
    rng = random.Random(SEED)
    ahora = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    with _conexion() as conexion:
        ids = _insertar_tripulacion(conexion)
        conexion.execute("DELETE FROM telemetria_continua")
        conexion.execute("DELETE FROM registros_discretos")

        for perfil in TRIPULACION:
            id_astronauta = ids[perfil["nombre"]]
            for indice in range(20):
                momento = ahora - timedelta(minutes=19 - indice)
                lectura = _generar_telemetria(id_astronauta, perfil, indice, momento, rng)
                columnas = ", ".join(lectura)
                marcadores = ", ".join("?" for _ in lectura)
                conexion.execute(
                    f"INSERT INTO telemetria_continua ({columnas}) VALUES ({marcadores})",
                    tuple(lectura.values()),
                )
                conexion.execute(
                    """
                    INSERT INTO registros_discretos
                        (id_astronauta, timestamp, urinary_calcium_mg_dl,
                         lymphocytes_count, winscat_cognitive_score, mood_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    _generar_discreto(
                        id_astronauta,
                        perfil,
                        indice,
                        ahora - timedelta(hours=12 * (19 - indice)),
                        rng,
                    ),
                )


def insertar_lectura_en_vivo(
    id_astronauta: int,
    timestamp: datetime | None = None,
    **valores: Any,
) -> int:
    """Inserta una lectura de telemetría y devuelve su identificador.

    Se pueden proporcionar valores concretos por nombre de columna; los campos
    omitidos se simulan a partir de la línea base del astronauta.
    """
    crear_esquema()
    with _conexion() as conexion:
        fila = conexion.execute(
            "SELECT * FROM tripulacion WHERE id_astronauta = ?",
            (id_astronauta,),
        ).fetchone()
        if fila is None:
            raise ValueError(f"El astronauta {id_astronauta} no existe")

        rng = random.Random()
        lectura = _generar_telemetria(
            id_astronauta,
            dict(fila),
            20,
            timestamp or datetime.now(timezone.utc),
            rng,
        )
        for columna in TELEMETRIA_COLUMNAS:
            if columna in valores:
                lectura[columna] = valores[columna]
        if "heart_rate" in valores and "rr_interval_sec" not in valores:
            lectura["rr_interval_sec"] = round(60.0 / float(lectura["heart_rate"]), 4)
        lectura["integrity_hash"] = _hash_telemetria(lectura)

        columnas = ", ".join((*TELEMETRIA_COLUMNAS, "integrity_hash"))
        marcadores = ", ".join("?" for _ in lectura)
        cursor = conexion.execute(
            f"INSERT INTO telemetria_continua ({columnas}) VALUES ({marcadores})",
            tuple(lectura[columna] for columna in (*TELEMETRIA_COLUMNAS, "integrity_hash")),
        )
        return int(cursor.lastrowid)


if __name__ == "__main__":
    inicializar_datos()
    print(f"Base inicializada en {DB_PATH}")
