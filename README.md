# Kubernetes Multi-Service & Ingress Project (ID: 68130239)

**ผู้จัดทำ:** Yutthasatr Khumkhonsue (รหัสนักศึกษา: `68130239`)  
**โดเมนที่ให้บริการ:** `www.id-239.com` และ `admin.id-239.com`

---

## 1. สถาปัตยกรรมระบบ (Architecture)

```text
[Browser: Windows / Linux] (/etc/hosts -> 192.168.1.20)
         │
         ▼
[External Nginx LB: k8s-lb (192.168.1.20:80)]
         │  (proxy_pass -> 192.168.1.11:31080, 192.168.1.12:31080)
         ▼
[NGINX Ingress Controller (Namespace: ingress-nginx, NodePort: 31080)]
         │
         ├── www.id-239.com/about       ──► svc-about    ──► Pod: app-about (Nginx + ConfigMap)
         ├── www.id-239.com/research    ──► svc-research ──► Pod: app-research (Python + PVC)
         ├── www.id-239.com/api/<msg>   ──► svc-api      ──► Pod: app-api (Python + ConfigMap)
         └── admin.id-239.com (/)       ──► svc-research ──► Pod: app-research (/edit -> PVC)
```

---

## 2. โครงสร้างไฟล์ใน Repository

```text
68130239/
├── apps/                        # ซอร์สโค้ดของแอปพลิเคชันทั้งหมด (Mount ผ่าน ConfigMap)
│   ├── app-about/               # index.html, about.html, avatar.svg
│   ├── app-research/            # server.py (/research และ /edit บันทึกลง PVC)
│   └── app-api/                 # server.py (/api/<ข้อความ> แสดงตัวใหญ่กลางจอ)
├── k8s/                         # Kubernetes Manifests
│   ├── 00-namespace.yaml        # Namespace: id-239
│   ├── 01-storage.yaml          # PersistentVolume + PersistentVolumeClaim
│   ├── 02-app-about.yaml        # ConfigMap (nginx.conf) + Deployment + Service
│   ├── 03-app-research.yaml     # Deployment + Service (Mount PVC /data)
│   ├── 04-app-api.yaml          # Deployment + Service
│   └── 05-ingress.yaml          # Ingress Rules (www.id-239.com & admin.id-239.com)
├── configs/
│   ├── etc-hosts-linux.txt      # ตัวอย่าง /etc/hosts สำหรับ Linux และ Windows
│   └── k8s-lb-ingress.conf      # คอนฟิก Nginx บนเครื่อง k8s-lb (192.168.1.20)
├── scripts/
│   ├── node-prereq.sh           # สคริปต์เตรียม Ubuntu 24.04 (containerd + kubeadm)
│   ├── deploy.sh                # สคริปต์ Deploy บน Linux (k8s-control)
│   ├── deploy.bat               # Batch Script สำหรับ Deploy จาก Windows
│   ├── win-setup-hosts.bat      # สคริปต์เพิ่มโดเมนลงไฟล์ hosts ของ Windows อัตโนมัติ
│   └── verify.sh                # สคริปต์ตรวจสอบสถานะ K8s และทดสอบ HTTP
└── docs/
    ├── VMWARE_WINDOWS_SETUP.md  # คู่มือตั้งค่า VMware บน Windows และสร้าง Cluster ตั้งแต่ต้น
    ├── REPORT_GUIDE.md          # แนวทางจัดทำรายงาน PDF (สิ่งที่ส่งข้อ 1)
    └── TEST_EVIDENCE_GUIDE.md   # แนวทางแคปหน้าจอการทดสอบทุก Service (สิ่งที่ส่งข้อ 3)
```

---

## 3. ขั้นตอนการ Deploy ตั้งแต่ต้นจนใช้งานได้

> **หากยังไม่มี Cluster บน VMware (Windows):** ทำตามคู่มือ [docs/VMWARE_WINDOWS_SETUP.md](./docs/VMWARE_WINDOWS_SETUP.md) เพื่อตั้งค่า `VMnet8`, สร้าง 4 VMs และรัน `kubeadm` ก่อนเริ่มขั้นตอนที่ 1 ด้านล่างครับ

### ขั้นตอนที่ 1: Deploy บน Kubernetes Cluster (`k8s-control`)
- **วิธีอัตโนมัติ (แนะนำ):**
  - จาก Windows: ดับเบิลคลิก `scripts/deploy.bat` (แก้ `CONTROL_USER` ให้ตรงกับชื่อผู้ใช้บน `k8s-control`)
  - หรือรันบน `k8s-control` โดยตรง:
    ```bash
    chmod +x scripts/*.sh
    bash scripts/deploy.sh
    ```
*(สคริปต์จะติดตั้ง NGINX Ingress Controller ให้อัตโนมัติหากยังไม่มี, ตั้ง NodePort เป็น `31080`, สร้าง ConfigMap จากโฟลเดอร์ `apps/` และ Apply ไฟล์ใน `k8s/` ทั้งหมด)*

### ขั้นตอนที่ 2: ตั้งค่า External Load Balancer (`k8s-lb` : `192.168.1.20`)
คัดลอกคอนฟิกจาก `configs/k8s-lb-ingress.conf` ไปวางบนเครื่อง **`k8s-lb`**:
```bash
sudo tee /etc/nginx/conf.d/id-239-ingress.conf << 'EOF'
upstream k8s_ingress_nodes {
    server 192.168.1.11:31080 max_fails=2 fail_timeout=5s;
    server 192.168.1.12:31080 max_fails=2 fail_timeout=5s;
}

server {
    listen 80;
    server_name www.id-239.com admin.id-239.com;

    access_log /var/log/nginx/id-239-access.log;
    error_log  /var/log/nginx/id-239-error.log;

    location / {
        proxy_pass http://k8s_ingress_nodes;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
sudo nginx -t && sudo systemctl reload nginx
```

### ขั้นตอนที่ 3: ตั้งค่า `/etc/hosts` (บน Linux) และ `hosts` (บน Windows)
- **บน Linux:** เพิ่มบรรทัดนี้ใน `/etc/hosts`:
  ```text
  192.168.1.20 www.id-239.com admin.id-239.com
  ```
- **บน Windows:** คลิกขวาที่ `scripts/win-setup-hosts.bat` -> **Run as administrator** (หรือเปิด Notepad แบบ Admin แก้ไขไฟล์ `C:\Windows\System32\drivers\etc\hosts`) เพื่อเพิ่ม:
  ```text
  192.168.1.20 www.id-239.com admin.id-239.com
  ```

### ขั้นตอนที่ 4: วิธีเปลี่ยนรูปโปรไฟล์จริงในหน้า `/about` (ถ้าต้องการ)
วางไฟล์รูปของคุณ (เช่น `avatar.svg` หรือแก้ไข `apps/app-about/about.html` ให้ชี้ไปที่ `photo.jpg`) แล้วรัน `bash scripts/deploy.sh` ใหม่อีกครั้ง ConfigMap จะอัปเดตให้อัตโนมัติ
*(หากเปลี่ยนไฟล์ภาพ อย่าลืมรัน `kubectl rollout restart deployment/app-about -n id-239` เพื่อให้ Nginx โหลดไฟล์ใหม่ทันที)*

---

## 4. การตรวจสอบการทำงาน
รันสคริปต์ตรวจสอบบน `k8s-control`:
```bash
bash scripts/verify.sh
```
จากนั้นเปิดเบราว์เซอร์ทดสอบทั้ง 4 URL:
1. `http://www.id-239.com/about`
2. `http://www.id-239.com/research`
3. `http://www.id-239.com/api/Hello%20Kubernetes`
4. `http://admin.id-239.com`
