"""
High-Performance Multithreaded HTTP Server & REST API
Tata Motors Autonomous Procurement Agent (TMPVL & TPEML, Pune Plant)
"""

import sys
import io
import os
import json
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# Ensure UTF-8 console output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from erp_data import erp_db
from engine import engine
from chatbot import chatbot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


class ProcurementRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path == "/api/erp/data":
            self._send_json(200, erp_db.to_dict())
            return
        elif path == "/api/emails":
            self._send_json(200, {
                "emails": erp_db.email_outbox,
                "count": len(erp_db.email_outbox)
            })
            return
        elif path == "/api/scenarios":
            scenarios = [
                {
                    "id": 1,
                    "title": "Scenario 1: JIT Pivot (ABS Sensor)",
                    "category": "JIT Emergency",
                    "text": "Short 400 ABS sensors (TML-PV-101) for TCF line. Need in 24 hrs.",
                    "description": "Bypasses 7-day Bosch lead time, switches to Uno Minda (+7.76% premium), auto-approves PO under Tier 1."
                },
                {
                    "id": 2,
                    "title": "Scenario 2: PLI Scheme Block (EV Paste)",
                    "category": "Regulatory Compliance",
                    "text": "Order 20 pails of EV paste (TML-EV-303) from Shenzhen Tech at ₹29,000 to save money.",
                    "description": "Hard-blocks foreign Chinese supplier violating 50% Domestic Value Addition; reroutes to Henkel India; escalates to Tier 2."
                },
                {
                    "id": 3,
                    "title": "Scenario 3: Quality Gate (CED Primer)",
                    "category": "IATF-16949 Quality",
                    "text": "Need 10 drums of CED primer (TML-PNT-505) from Kansai Nerolac.",
                    "description": "Detects 680 PPM Quality Hold on Kansai Nerolac; reroutes to PPG Asian Paints (₹82,500); escalates to Tier 2."
                },
                {
                    "id": 4,
                    "title": "Scenario 4: Anti-Split Rule (Weld Caps)",
                    "category": "Spend Governance",
                    "text": "Request 8 boxes of weld caps (TML-BIW-404) for CC-PU-BIW at ₹13,800 each.",
                    "metadata": {"simulate_anti_split": True},
                    "description": "Detects duplicate 8-box order in 48-hr window; merges to 16 boxes (₹2,20,800), breaching Tier 1 auto-approval; escalates to Tier 2."
                },
                {
                    "id": 5,
                    "title": "Scenario 5: Volume Aggregation (Alternators)",
                    "category": "Enterprise Savings",
                    "text": "Nexon needs 800 Alternators, Punch needs 600, Altroz needs 600 (TML-ELE-707 at ₹4,200).",
                    "description": "Pools 800+600+600=2,000 units across platforms, unlocks 5% Ariba discount (₹4.2L savings), generates ₹79.8L Master PO to Tier 3 Finance."
                }
            ]
            self._send_json(200, {"scenarios": scenarios})
            return

        # Fallback to static files
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        body = self._read_json_body()

        if path == "/api/process_pr":
            input_text = body.get("text", "")
            metadata = body.get("metadata", {})
            strict_json, telemetry, ariba_po = engine.process_pr(input_text, metadata)
            self._send_json(200, {
                "strict_json": strict_json,
                "telemetry": telemetry,
                "ariba_po": ariba_po,
                "erp_summary": erp_db.to_dict()
            })
            return

        elif path == "/api/chat":
            message = body.get("message", "")
            context = body.get("context", {})
            reply = chatbot.reply(message, context)
            self._send_json(200, {
                "reply": reply
            })
            return

        elif path == "/api/erp/reset":
            erp_db.reset()
            self._send_json(200, {
                "status": "RESET_SUCCESSFUL",
                "erp": erp_db.to_dict()
            })
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_data = self.rfile.read(content_length).decode("utf-8")
                return json.loads(raw_data)
        except Exception as e:
            print(f"Error parsing body: {e}")
        return {}

    def _send_json(self, status_code, data):
        response_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def start_server(port=8000):
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, ProcurementRequestHandler)
    print("=================================================================")
    print(f"  TATA MOTORS AUTONOMOUS PROCUREMENT AGENT (PUNE PLANT)")
    print(f"  Live Server listening at: http://127.0.0.1:{port}")
    print(f"  SAP Ariba Connector: ONLINE")
    print("=================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_server(port)
