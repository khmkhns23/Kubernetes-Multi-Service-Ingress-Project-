@echo off
REM ==========================================================
REM เพิ่ม www.id-239.com และ admin.id-239.com ลงใน Windows hosts
REM วิธีใช้: คลิกขวาไฟล์นี้ -> Run as administrator
REM ==========================================================

set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts
set ENTRY=192.168.1.20 www.id-239.com admin.id-239.com

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Please right-click this file and select "Run as administrator"!
    pause
    exit /b 1
)

findstr /C:"www.id-239.com" "%HOSTS_FILE%" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Entry for www.id-239.com already exists in hosts file.
) else (
    echo.>> "%HOSTS_FILE%"
    echo %ENTRY%>> "%HOSTS_FILE%"
    echo [OK] Added: %ENTRY%
)

ipconfig /flushdns >nul
echo [OK] DNS cache flushed.
pause
