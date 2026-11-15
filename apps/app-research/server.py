import html
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

DATA_FILE = os.environ.get("RESEARCH_FILE", "/data/research.txt")

DEFAULT_RESEARCH = """หัวข้อวิจัย (ตัวอย่าง - กรุณาแก้ไขผ่าน http://admin.id-239.com):
การศึกษาประสิทธิภาพการจัดการ Microservices ด้วย Kubernetes และ Ingress Controller

บทคัดย่อ / สรุปงานวิจัย (300 - 500 คำ):
ในยุคปัจจุบัน การพัฒนาซอฟต์แวร์ขนาดใหญ่ได้เปลี่ยนผ่านจากสถาปัตยกรรมแบบ Monolithic มาสู่สถาปัตยกรรมแบบ Microservices เพื่อให้สามารถพัฒนา ปรับปรุง และขยายระบบ (Scalability) ได้อย่างอิสระและรวดเร็ว อย่างไรก็ตาม การบริหารจัดการ Container จำนวนมากในสภาพแวดล้อมจริงยังคงมีความซับซ้อน ทั้งในด้านการจัดสรรทรัพยากร การกระจายภาระงาน (Load Balancing) การตรวจสอบสถานะการทำงานอัตโนมัติ (Self-healing) และการกำหนดเส้นทางเครือข่าย (Routing) งานวิจัยฉบับนี้จึงมุ่งเน้นศึกษาและประเมินประสิทธิภาพของแพลตฟอร์ม Kubernetes ซึ่งเป็นเครื่องมือมาตรฐานสำหรับการจัดการ Container Orchestration ร่วมกับ NGINX Ingress Controller เพื่อรองรับการให้บริการหลายแอปพลิเคชันภายใต้คลัสเตอร์เดียวกัน

ในการทดลองได้ออกแบบระบบจำลองประกอบด้วย Node จำนวน 3 เครื่อง ได้แก่ Control Plane 1 เครื่อง และ Worker Node 2 เครื่อง โดยทำการติดตั้งบริการที่แตกต่างกัน เช่น บริการแสดงข้อมูลส่วนบุคคล บริการจัดการบทความที่มีการบันทึกข้อมูลแบบถาวรผ่าน PersistentVolumeClaim (PVC) และบริการ API ประมวลผลข้อความ จากนั้นทำการกำหนดกฎการกระจายทราฟฟิกทั้งในรูปแบบ Path-based Routing และ Host-based Routing ผ่าน Ingress เพื่อแยกเส้นทางการเข้าถึงของผู้ใช้งานทั่วไปและผู้ดูแลระบบออกจากกันอย่างชัดเจน

ผลการศึกษาพบว่า การใช้ Kubernetes ช่วยลดเวลาในการติดตั้งและอัปเดตเวอร์ชันของบริการได้อย่างมีนัยสำคัญด้วยกลไก Rolling Update โดยไม่เกิด Downtime อีกทั้งเมื่อจำลองสถานการณ์ที่ Pod เกิดความขัดข้อง ระบบสามารถสร้าง Pod ใหม่ขึ้นมาทดแทนได้อัตโนมัติภายในไม่กี่วินาที นอกจากนี้ การใช้ PersistentVolume ร่วมกับ PersistentVolumeClaim ยังช่วยให้ข้อมูลสำคัญที่ถูกแก้ไขจากฝั่งผู้ดูแลระบบยังคงอยู่ครบถ้วนแม้มีการรีสตาร์ทหรือสร้าง Pod ใหม่ สรุปได้ว่าสถาปัตยกรรม Kubernetes ร่วมกับ Ingress Controller มีความเหมาะสมอย่างยิ่งสำหรับการนำไปประยุกต์ใช้ในระบบการให้บริการยุคใหม่ที่ต้องการความเสถียร ความยืดหยุ่น และความปลอดภัยในการแบ่งแยกสิทธิ์การเข้าถึงบริการต่างๆ
"""


def ensure_data_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(DEFAULT_RESEARCH.strip())


def read_research():
    ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return f.read()


def write_research(content):
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content)


class ResearchHandler(BaseHTTPRequestHandler):
    def send_html(self, status_code, body):
        data = body.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        host = self.headers.get("Host", "").lower()
        query = urllib.parse.parse_qs(parsed.query)

        # ถ้าเข้าผ่าน admin.id-239.com หรือ path /edit ให้แสดงหน้าแก้ไข
        if parsed.path in ("/edit", "/edit/") or (parsed.path == "/" and host.startswith("admin.")):
            content = html.escape(read_research())
            saved_banner = (
                '<div class="alert">บันทึกข้อมูลสรุปงานวิจัยเรียบร้อยแล้ว! '
                '<a href="http://www.id-239.com/research" target="_blank">ดูผลลัพธ์ที่ www.id-239.com/research</a></div>'
                if query.get("saved") == ["1"]
                else ""
            )
            page = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Admin - แก้ไขสรุปงานวิจัย (68130239)</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px 16px; }}
    .container {{ max-width: 820px; margin: auto; background: #1e293b; padding: 32px; border-radius: 16px; border: 1px solid #334155; }}
    h1 {{ color: #a78bfa; margin-top: 0; }}
    .alert {{ background: #065f46; color: #d1fae5; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; }}
    .alert a {{ color: #6ee7b7; font-weight: bold; }}
    textarea {{ width: 100%; height: 340px; padding: 14px; border-radius: 10px; border: 1px solid #475569; background: #0f172a; color: #f8fafc; font-size: 1rem; line-height: 1.6; box-sizing: border-box; }}
    .actions {{ margin-top: 16px; display: flex; gap: 12px; align-items: center; }}
    button {{ background: #7c3aed; color: #fff; border: none; padding: 12px 24px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; }}
    button:hover {{ background: #6d28d9; }}
    .meta {{ color: #94a3b8; font-size: 0.9rem; margin-left: auto; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Admin Panel: แก้ไขสรุปงานวิจัย</h1>
    <p style="color:#94a3b8;">Service: <strong>app-research (/edit)</strong> &bull; บันทึกลง PersistentVolumeClaim (PVC)</p>
    {saved_banner}
    <form method="POST" action="/edit">
      <textarea name="content" required>{content}</textarea>
      <div class="actions">
        <button type="submit">บันทึกข้อมูล (Save)</button>
        <span class="meta">Host: {html.escape(host)}</span>
      </div>
    </form>
  </div>
</body>
</html>"""
            self.send_html(200, page)
            return

        # หน้าแสดงผล /research
        content = read_research()
        word_count = len(content.split())
        escaped_content = html.escape(content).replace("\n", "<br>")
        page = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Research Summary - 68130239</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px 16px; }}
    .container {{ max-width: 820px; margin: auto; background: #1e293b; padding: 36px; border-radius: 16px; border: 1px solid #334155; line-height: 1.8; }}
    h1 {{ color: #38bdf8; margin-top: 0; }}
    .badge {{ display: inline-block; background: #0284c7; padding: 4px 12px; border-radius: 999px; font-size: 0.85rem; margin-bottom: 16px; }}
    .content {{ background: #0f172a; padding: 24px; border-radius: 12px; border: 1px solid #334155; font-size: 1.05rem; }}
    .footer {{ margin-top: 24px; display: flex; justify-content: space-between; color: #94a3b8; font-size: 0.9rem; }}
    a {{ color: #38bdf8; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>สรุปงานวิจัยวิชาสัมมนา</h1>
    <div class="badge">Service: app-research &bull; Yutthasatr Khumkhonsue (68130239)</div>
    <div class="content">{escaped_content}</div>
    <div class="footer">
      <span>ความยาวโดยประมาณ: {word_count} คำ/กลุ่มคำ</span>
      <span><a href="/">หน้าแรก</a> | <a href="/about">About</a> | <a href="http://admin.id-239.com">แก้ไขบทความ (Admin)</a></span>
    </div>
  </div>
</body>
</html>"""
        self.send_html(200, page)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/edit", "/edit/", "/"):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            form = urllib.parse.parse_qs(raw)
            new_content = form.get("content", [""])[0].strip()
            if new_content:
                write_research(new_content)
            self.send_response(303)
            self.send_header("Location", "/edit?saved=1")
            self.end_headers()
            return
        self.send_html(404, "Not Found")


if __name__ == "__main__":
    ensure_data_file()
    server = HTTPServer(("0.0.0.0", 8080), ResearchHandler)
    print("app-research listening on port 8080...")
    server.serve_forever()
