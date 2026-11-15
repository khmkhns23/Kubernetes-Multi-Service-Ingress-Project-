# แนวทางจัดทำรายงาน PDF (สิ่งที่ส่งข้อ 1)

เพื่อให้รายงาน PDF ครบถ้วนตามเกณฑ์ที่อาจารย์กำหนด แนะนำให้จัดเรียงหัวข้อดังนี้:

## บทที่ 1: ภาพรวมสถาปัตยกรรมระบบและการเตรียม VMware Cluster (Windows)
- การตั้งค่า VMware Virtual Network (`VMnet8` NAT: `192.168.1.0/24`, Gateway `192.168.1.2`) และการสร้าง 4 VMs (`k8s-control`, `k8s-worker1`, `k8s-worker2`, `k8s-lb`) ดูรายละเอียดจาก `docs/VMWARE_WINDOWS_SETUP.md`
- แผนภาพระบบ (Client -> `/etc/hosts` -> `k8s-lb (192.168.1.20)` -> `NGINX Ingress Controller (31080)` -> `ClusterIP Services` -> `Pods` -> `PVC`)
- ตารางสรุป IP, Port, Hostname และหน้าที่ของแต่ละ Service (`app-about`, `app-research`, `app-api`)

## บทที่ 2: ไฟล์ Kubernetes Manifests และคอนฟิกที่เกี่ยวข้อง
นำโค้ด/เนื้อหาของไฟล์เหล่านี้มาใส่ในรายงาน:
1. `k8s/00-namespace.yaml` (Namespace `id-239`)
2. `k8s/01-storage.yaml` (PV และ PVC สำหรับเก็บสรุปงานวิจัย)
3. `k8s/02-app-about.yaml` (ConfigMap + Deployment + Service `svc-about`)
4. `k8s/03-app-research.yaml` (Deployment + Service `svc-research` + Volume Mount `/data`)
5. `k8s/04-app-api.yaml` (Deployment + Service `svc-api`)
6. `k8s/05-ingress.yaml` (Ingress Rules สำหรับ `www.id-239.com` และ `admin.id-239.com`)
7. ไฟล์ `/etc/hosts` ของ Linux (และ `C:\Windows\System32\drivers\etc\hosts`)
8. ไฟล์คอนฟิก Nginx `/etc/nginx/conf.d/id-239-ingress.conf` บน `k8s-lb`

## บทที่ 3: ขั้นตอนการสั่งการ `kubectl`
แสดงคำสั่งที่ใช้ในการ Deploy ตั้งแต่ต้น:
- การติดตั้ง NGINX Ingress Controller และตั้ง NodePort `31080`
- การสร้าง ConfigMap จากโค้ดด้วย `kubectl create configmap ...`
- การ Apply Manifests (`kubectl apply -f k8s/...`)

## บทที่ 4: การตรวจสอบการทำงาน (`kubectl get` และ `kubectl describe`)
รันคำสั่งเหล่านี้บน `k8s-control` แล้วแคปภาพหน้าจอผลลัพธ์มาใส่ในรายงาน:
```bash
# 1. ดูสถานะภาพรวมทั้งหมดใน Namespace id-239
kubectl get all,ingress,pv,pvc,cm -n id-239 -o wide

# 2. ดูรายละเอียดกฎของ Ingress (Host & Path Routing)
kubectl describe ingress id-239-ingress -n id-239

# 3. ดูรายละเอียด Pod และ PVC ว่า Bound และ Mount สำเร็จ
kubectl describe pvc research-pvc-239 -n id-239
kubectl describe pod -l app=app-research -n id-239

# 4. ดู Endpoints ของทุก Service
kubectl get endpoints -n id-239
```
