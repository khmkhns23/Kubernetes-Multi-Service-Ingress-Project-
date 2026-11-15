import html
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # รองรับทั้ง /api/<ข้อความ> และ /<ข้อความ> (เผื่อกรณี rewrite)
        if path.startswith("/api/"):
            raw_msg = path[len("/api/"):]
        elif path == "/api":
            raw_msg = "กรุณาพิมพ์ข้อความต่อท้าย เช่น /api/Hello"
        else:
            raw_msg = path.lstrip("/") or "กรุณาพิมพ์ข้อความต่อท้าย เช่น /api/Hello"

        message = urllib.parse.unquote(raw_msg)
        safe_msg = html.escape(message)

        body = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>API Display - {safe_msg}</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
      color: #f8fafc;
      font-family: 'Segoe UI', Tahoma, sans-serif;
      text-align: center;
      padding: 24px;
    }}
    .big-text {{
      font-size: clamp(2.5rem, 8vw, 6.5rem);
      font-weight: 800;
      color: #38bdf8;
      text-shadow: 0 6px 30px rgba(56, 189, 248, 0.35);
      word-break: break-word;
      max-width: 90vw;
    }}
    .sub {{
      margin-top: 24px;
      color: #94a3b8;
      font-size: 1rem;
    }}
  </style>
</head>
<body>
  <div class="big-text">{safe_msg}</div>
  <div class="sub">Served by <strong>app-api</strong> &bull; ID: 68130239</div>
</body>
</html>"""
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), ApiHandler)
    print("app-api listening on port 8080...")
    server.serve_forever()
