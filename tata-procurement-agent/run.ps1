# Tata Motors Autonomous Procurement Agent Launcher
$Host.UI.RawUI.WindowTitle = "Tata Motors Autonomous Procurement Agent (Pune Plant)"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "  Starting Tata Motors Autonomous Procurement Agent" -ForegroundColor White
Write-Host "  Pune Manufacturing Plant (TMPVL & TPEML)" -ForegroundColor White
Write-Host "  Local Web Interface: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Cyan

Start-Process "http://127.0.0.1:8000"
python server.py 8000
