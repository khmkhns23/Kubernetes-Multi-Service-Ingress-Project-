# คู่มือการตั้งค่า VMware Workstation บน Windows และสร้าง Kubernetes Cluster (Ubuntu 24.04)

เอกสารนี้อธิบายขั้นตอนตั้งแต่การเตรียมระบบเครือข่าย VMware บนเครื่อง **Windows** ไปจนถึงการสร้าง Kubernetes Cluster 3 Nodes + External Load Balancer 1 Node ให้พร้อมสำหรับรันโปรเจกต์ `68130239`

---

## ขั้นตอนที่ 1: ตั้งค่า Virtual Network (`VMnet8` NAT) บน Windows

1. เปิดโปรแกรม **VMware Workstation Pro** -> ไปที่เมนู **Edit** -> **Virtual Network Editor...**
2. กดปุ่ม **Change Settings** (ด้านล่างขวา เพื่อขอสิทธิ์ Administrator)
3. เลือก **`VMnet8`** (Type: **NAT**) แล้วตั้งค่าดังนี้:
   - **Subnet IP:** `192.168.1.0`
   - **Subnet mask:** `255.255.255.0`
4. กดปุ่ม **NAT Settings...**:
   - **Gateway IP:** `192.168.1.2` -> กด **OK**
5. กด **OK** / **Apply** เพื่อบันทึก
6. ตรวจสอบบน Windows PowerShell ว่าการ์ดแลน `VMware Network Adapter VMnet8` ได้ IP `192.168.1.1`:
   ```powershell
   Get-NetIPAddress -InterfaceAlias "*VMnet8*" -AddressFamily IPv4
   ```

> **กรณีเปิด VPN บน Windows แล้วเชื่อมต่อ VM (`192.168.1.x`) ไม่ได้:**
> ให้รัน PowerShell (Run as Administrator) เพิ่ม Route ชี้ตรงไปยัง VMnet8 (แทน `<IfIndex>` ด้วยหมายเลข Interface ของ VMnet8 จาก `Get-NetAdapter`):
> ```powershell
> route add 192.168.1.10 mask 255.255.255.255 0.0.0.0 if <IfIndex>
> route add 192.168.1.11 mask 255.255.255.255 0.0.0.0 if <IfIndex>
> route add 192.168.1.12 mask 255.255.255.255 0.0.0.0 if <IfIndex>
> route add 192.168.1.20 mask 255.255.255.255 0.0.0.0 if <IfIndex>
> ```

---

## ขั้นตอนที่ 2: สร้าง Virtual Machines ทั้ง 4 เครื่อง (Ubuntu 24.04 LTS)

| ชื่อ VM | บทบาท | IP Address | CPU | RAM | Network |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `k8s-control` | Control Plane | `192.168.1.10` | 2 vCPU | 4096 MB | NAT (VMnet8) |
| `k8s-worker1` | Worker Node 1 | `192.168.1.11` | 2 vCPU | 2048 MB | NAT (VMnet8) |
| `k8s-worker2` | Worker Node 2 | `192.168.1.12` | 2 vCPU | 2048 MB | NAT (VMnet8) |
| `k8s-lb` | External Nginx LB | `192.168.1.20` | 1 vCPU | 1024 MB | NAT (VMnet8) |

### แก้ปัญหาหน้าจอ Ubuntu 24.04 ค้าง/Crash บน VMware (สำคัญสำหรับ Windows)
หากเปิด VM แล้วพบ Error `mks Exception 0xc0000005` หรือจอดำ ให้ปิด VM แล้วเปิดไฟล์ `.vmx` ของทุกเครื่องด้วย Notepad เพิ่ม/แก้ไขบรรทัดนี้:
```text
mks.enable3d = "FALSE"
```
*(หรือปิด **Accelerate 3D graphics** ใน VM Settings -> Display)*

---

## ขั้นตอนที่ 3: ตั้งค่า Network, Hostname และ `/etc/hosts` บนแต่ละ VM

> **ข้อควรระวังกรณี Clone VM:** หลัง Clone เสร็จ ต้องสร้าง `machine-id` ใหม่ และ **Flush IP เก่าทิ้ง** เพื่อป้องกันปัญหา `ens33` มี 2 IP ชนกัน!

รันบน **ทุกเครื่อง** (เปลี่ยน `<HOSTNAME>` และ `<NODE_IP>` ตามตารางด้านบน):

```bash
# 1. ตั้ง Hostname
sudo hostnamectl set-hostname <HOSTNAME>

# 2. สร้าง machine-id ใหม่ (จำเป็นมากถ้า Clone VM)
sudo rm -f /etc/machine-id /var/lib/dbus/machine-id
sudo systemd-machine-id-setup

# 3. ตั้งค่า /etc/hosts บนทุกเครื่อง
sudo tee /etc/hosts << 'EOF'
127.0.0.1 localhost
127.0.1.1 <HOSTNAME>

192.168.1.10 k8s-control
192.168.1.11 k8s-worker1
192.168.1.12 k8s-worker2
192.168.1.20 k8s-lb
EOF

# 4. ตั้งค่า Static IP ผ่าน Netplan (เช็คชื่อการ์ดแลนด้วย ip -br link เช่น ens33)
sudo rm -f /etc/netplan/*.yaml
sudo tee /etc/netplan/01-netcfg.yaml << 'EOF'
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      dhcp4: no
      addresses:
        - <NODE_IP>/24
      routes:
        - to: default
          via: 192.168.1.2
      nameservers:
        addresses:
          - 192.168.1.2
          - 8.8.8.8
EOF

sudo chmod 600 /etc/netplan/01-netcfg.yaml
sudo ip addr flush dev ens33
sudo netplan apply
ip -br addr show ens33
```

---

## ขั้นตอนที่ 4: สร้าง Kubernetes Cluster (`kubeadm` v1.31)

### 4.1 เตรียมระบบบน Control Plane และ Workers (`k8s-control`, `k8s-worker1`, `k8s-worker2`)
คัดลอกสคริปต์ `scripts/node-prereq.sh` ไปรันบนทั้ง 3 เครื่อง:
```bash
sudo bash scripts/node-prereq.sh
```
*(สคริปต์จะปิด Swap, ตั้งค่า Kernel/Sysctl, ติดตั้ง `containerd` พร้อม `SystemdCgroup = true` และติดตั้ง `kubelet`, `kubeadm`, `kubectl` v1.31)*

### 4.2 Initialize Control Plane (ทำเฉพาะ `k8s-control`)
```bash
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --apiserver-advertise-address=192.168.1.10

# ตั้งค่าให้ user ปกติใช้งาน kubectl ได้
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# ติดตั้ง Flannel CNI (Pod Network)
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

### 4.3 นำ Worker Nodes เข้าร่วมคลัสเตอร์ (ทำบน `k8s-worker1` และ `k8s-worker2`)
1. บน `k8s-control` รันเพื่อสร้างคำสั่ง Join:
   ```bash
   kubeadm token create --print-join-command
   ```
2. นำคำสั่งที่ได้ (เติม `sudo` ข้างหน้า) ไปรันบน `k8s-worker1` และ `k8s-worker2`
3. ตรวจสอบบน `k8s-control` จนทุก Node ขึ้น **`Ready`**:
   ```bash
   kubectl get nodes -o wide
   ```

---

## ขั้นตอนที่ 5: ตั้งค่า External Load Balancer (`k8s-lb`) และ Windows `hosts`

1. บน **`k8s-lb` (`192.168.1.20`)**: ติดตั้ง Nginx และเปิดใช้งานคอนฟิก `configs/k8s-lb-ingress.conf`:
   ```bash
   sudo apt update && sudo apt install -y nginx
   sudo rm -f /etc/nginx/sites-enabled/default
   # คัดลอกเนื้อหาจาก configs/k8s-lb-ingress.conf มาวางที่ /etc/nginx/conf.d/id-239-ingress.conf
   sudo nginx -t && sudo systemctl enable --now nginx
   ```
2. บน **Windows**: คลิกขวาที่ `scripts/win-setup-hosts.bat` แล้วเลือก **Run as administrator** เพื่อเพิ่ม:
   ```text
   192.168.1.20 www.id-239.com admin.id-239.com
   ```
   ลงใน `C:\Windows\System32\drivers\etc\hosts`
3. รัน `scripts/deploy.bat` (หรือ `bash scripts/deploy.sh` บน `k8s-control`) เพื่อติดตั้ง Ingress Controller และบริการทั้งหมดของ `68130239` ได้ทันที!
