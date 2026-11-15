import datetime
import hashlib
import http.server
import json
import os
import sqlite3


HOST = "0.0.0.0"
PORT = 8000
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "egle_mission.db")
WEB_ROOT = os.path.dirname(os.path.abspath(__file__))


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def connect_database():
    connection = sqlite3.connect(DATABASE, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = connect_database()
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS crew_profiles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                age INTEGER NOT NULL,
                weight REAL NOT NULL,
                sex TEXT NOT NULL,
                height REAL NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS telemetry_stream (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                astronaut_id TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                sha256_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS nasa_downlink_queue (
                packet_id TEXT PRIMARY KEY,
                timestamp_utc TEXT NOT NULL,
                category TEXT NOT NULL,
                summary TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                sha256_hash TEXT NOT NULL
            );
            """
        )
        connection.commit()
    finally:
        connection.close()


def network_ip():
    candidates = []
    try:
        for line in os.popen("ipconfig").read().splitlines():
            if ":" not in line:
                continue
            value = line.rsplit(":", 1)[1].strip()
            parts = value.split(".")
            if len(parts) != 4:
                continue
            try:
                if all(0 <= int(part) <= 255 for part in parts):
                    candidates.append(value)
            except ValueError:
                continue
    except OSError:
        return "unavailable"
    for candidate in candidates:
        if not candidate.startswith("127."):
            return candidate
    return candidates[0] if candidates else "unavailable"


def decode_json_field(row, field):
    result = dict(row)
    encoded = result.get(field)
    if encoded is not None:
        result[field[:-5] if field.endswith("_json") else field] = json.loads(encoded)
    return result


class MissionHubHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "EGLEMissionHub/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def request_path(self):
        return self.path.split("?", 1)[0]

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        if not raw:
            raise ValueError("Request body must contain JSON.")
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Request body is not valid JSON.") from error

    def do_GET(self):
        if self.request_path() == "/api/state":
            self.get_state()
            return
        super().do_GET()

    def get_state(self):
        connection = connect_database()
        try:
            crew = [dict(row) for row in connection.execute(
                "SELECT id, name, role, age, weight, sex, height, updated_at "
                "FROM crew_profiles ORDER BY name"
            )]
            latest = [decode_json_field(row, "payload_json") for row in connection.execute(
                """
                SELECT stream.id, stream.astronaut_id, stream.timestamp_utc,
                       stream.payload_json, stream.sha256_hash
                FROM telemetry_stream AS stream
                WHERE stream.id = (
                    SELECT MAX(newer.id)
                    FROM telemetry_stream AS newer
                    WHERE newer.astronaut_id = stream.astronaut_id
                )
                ORDER BY stream.timestamp_utc DESC
                """
            )]
            downlink = [decode_json_field(row, "payload_json") for row in connection.execute(
                """
                SELECT packet_id, timestamp_utc, category, summary,
                       payload_json, status, sha256_hash
                FROM nasa_downlink_queue
                ORDER BY timestamp_utc DESC
                LIMIT 50
                """
            )]
            self.send_json({"crew": crew, "latest_telemetry": latest, "downlink": downlink})
        finally:
            connection.close()

    def do_POST(self):
        path = self.request_path()
        try:
            payload = self.read_json()
            if path == "/api/crew":
                self.post_crew(payload)
            elif path == "/api/telemetry":
                self.post_telemetry(payload)
            elif path == "/api/downlink":
                self.post_downlink(payload)
            else:
                self.send_json({"ok": False, "error": "Not found."}, 404)
        except ValueError as error:
            self.send_json({"ok": False, "error": str(error)}, 400)
        except sqlite3.Error as error:
            self.send_json({"ok": False, "error": "Database error: " + str(error)}, 500)

    def post_crew(self, payload):
        if not isinstance(payload, list):
            raise ValueError("Crew endpoint expects a JSON array.")
        connection = connect_database()
        try:
            for crew in payload:
                if not isinstance(crew, dict):
                    raise ValueError("Each crew profile must be an object.")
                required = ("id", "name", "role", "age", "weight", "sex", "height")
                if any(field not in crew for field in required):
                    raise ValueError("Crew profiles require id, name, role, age, weight, sex, and height.")
                connection.execute(
                    """
                    INSERT INTO crew_profiles
                        (id, name, role, age, weight, sex, height, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name=excluded.name, role=excluded.role, age=excluded.age,
                        weight=excluded.weight, sex=excluded.sex, height=excluded.height,
                        updated_at=excluded.updated_at
                    """,
                    (
                        str(crew["id"]), str(crew["name"]), str(crew["role"]),
                        int(crew["age"]), float(crew["weight"]), str(crew["sex"]),
                        float(crew["height"]), str(crew.get("updated_at") or utc_now()),
                    ),
                )
            connection.commit()
        finally:
            connection.close()
        self.send_json({"ok": True, "count": len(payload)})

    def post_telemetry(self, payload):
        if not isinstance(payload, dict) or not payload.get("astronautId"):
            raise ValueError("Telemetry requires astronautId and telemetry.")
        telemetry = payload.get("telemetry")
        if not isinstance(telemetry, dict):
            raise ValueError("Telemetry must be a JSON object.")
        payload_json = json.dumps(telemetry, sort_keys=True)
        digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        connection = connect_database()
        try:
            connection.execute(
                """
                INSERT INTO telemetry_stream
                    (astronaut_id, timestamp_utc, payload_json, sha256_hash)
                VALUES (?, ?, ?, ?)
                """,
                (str(payload["astronautId"]), str(payload.get("_ts") or utc_now()), payload_json, digest),
            )
            connection.commit()
        finally:
            connection.close()
        self.send_json({"ok": True, "sha256": digest})

    def post_downlink(self, payload):
        packets = payload if isinstance(payload, list) else [payload]
        if not packets or any(not isinstance(packet, dict) for packet in packets):
            raise ValueError("Downlink endpoint expects a packet object or array.")
        connection = connect_database()
        try:
            for index, packet in enumerate(packets):
                packet_id = str(packet.get("id") or (utc_now() + "-" + str(index)))
                timestamp = str(packet.get("timestamp") or utc_now())
                packet_payload = packet.get("payload")
                payload_json = json.dumps(packet_payload, sort_keys=True)
                digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
                connection.execute(
                    """
                    INSERT INTO nasa_downlink_queue
                        (packet_id, timestamp_utc, category, summary, payload_json, status, sha256_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(packet_id) DO UPDATE SET
                        timestamp_utc=excluded.timestamp_utc, category=excluded.category,
                        summary=excluded.summary, payload_json=excluded.payload_json,
                        status=excluded.status, sha256_hash=excluded.sha256_hash
                    """,
                    (
                        packet_id, timestamp, str(packet.get("category") or ""),
                        str(packet.get("summary") or ""), payload_json,
                        str(packet.get("status") or "[LOCAL NON-VOLATILE BUFFER]"), digest,
                    ),
                )
            connection.commit()
        finally:
            connection.close()
        self.send_json({"ok": True})

    def do_DELETE(self):
        if self.request_path() != "/api/downlink/sent":
            self.send_json({"ok": False, "error": "Not found."}, 404)
            return
        connection = connect_database()
        try:
            cursor = connection.execute(
                "DELETE FROM nasa_downlink_queue "
                "WHERE status = '[AUTO-TRANSMITTED TO NASA MCC]'"
            )
            connection.commit()
            self.send_json({"ok": True, "deleted": cursor.rowcount})
        finally:
            connection.close()

    def log_message(self, format_string, *args):
        print("[HTTP] " + (format_string % args))


def main():
    initialize_database()
    server = http.server.ThreadingHTTPServer((HOST, PORT), MissionHubHandler)
    print("EGLE Mission Hub started.")
    print("SQLite database: " + DATABASE + " (ready)")
    print("Local URL: http://localhost:8000")
    print("Network URL: http://" + network_ip() + ":8000")
    print("Serving static files from: " + WEB_ROOT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEGLE Mission Hub stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
