@echo off
title Tata Motors Autonomous Procurement Agent (Pune Plant)
cd /d "%~dp0"
echo =========================================================================
echo   Starting Tata Motors Autonomous Procurement Agent
echo   Pune Manufacturing Plant (TMPVL ^& TPEML)
echo   Local Web Interface: http://127.0.0.1:8000
echo =========================================================================
start http://127.0.0.1:8000
python server.py 8000
pause
