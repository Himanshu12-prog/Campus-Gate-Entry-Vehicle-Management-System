@echo off
title Campus Gate Entry & Vehicle Management System
color 0A

echo ======================================================================
echo    CAMPUS GATE ENTRY & VEHICLE MANAGEMENT SYSTEM (PRODUCTION SERVER)
echo ======================================================================
echo.
echo [1/2] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.9+.
    pause
    exit /b
)

echo [2/2] Launching Local Server...
echo Server starting at http://127.0.0.1:5000
echo.
echo Press CTRL+C in this window to stop the server anytime.
echo ======================================================================
echo.

start "" "http://127.0.0.1:5000"
python app.py

pause
