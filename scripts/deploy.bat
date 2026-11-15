@echo off
REM ==========================================================
REM Batch Script สำหรับ Deploy จากเครื่อง Windows ไปยัง k8s-control
REM การใช้งาน: ดับเบิลคลิก หรือรัน deploy.bat ใน PowerShell/CMD
REM ==========================================================

set CONTROL_USER=yut
set CONTROL_IP=192.168.1.10

echo ==========================================================
echo  [1/2] Uploading project 68130239 to %CONTROL_USER%@%CONTROL_IP% ...
echo ==========================================================
scp -r "%~dp0.." %CONTROL_USER%@%CONTROL_IP%:~/68130239

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] SCP upload failed. Check SSH connectivity to %CONTROL_IP%.
    pause
    exit /b 1
)

echo ==========================================================
echo  [2/2] Running deploy.sh on k8s-control ...
echo ==========================================================
ssh %CONTROL_USER%@%CONTROL_IP% "sed -i 's/\r$//' ~/68130239/scripts/*.sh && chmod +x ~/68130239/scripts/*.sh && bash ~/68130239/scripts/deploy.sh"

echo.
echo ==========================================================
echo  Done! Remember to configure /etc/hosts and k8s-lb Nginx!
echo ==========================================================
pause
