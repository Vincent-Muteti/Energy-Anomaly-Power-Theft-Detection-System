# Power Theft Detection System - Quick Start Script (PowerShell)
# ==============================================================

Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "Power Theft Detection System - Setup`n" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "`nVirtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
Write-Host "pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed" -ForegroundColor Green

# Verify installation
Write-Host "`nRunning deployment verification tests..." -ForegroundColor Yellow
Write-Host "==========================================`n" -ForegroundColor Cyan
python test_deployment.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nError: Some tests failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n==========================================`n" -ForegroundColor Cyan
Write-Host "Setup complete!`n" -ForegroundColor Green

Write-Host "Next steps:`n" -ForegroundColor Cyan
Write-Host "  1. Activate virtual environment:" -ForegroundColor Yellow
Write-Host "     .\venv\Scripts\Activate.ps1`n" -ForegroundColor White

Write-Host "  2. Test the detector:" -ForegroundColor Yellow
Write-Host "     python power_theft_detector.py`n" -ForegroundColor White

Write-Host "  3. Start the API server:" -ForegroundColor Yellow
Write-Host "     python app.py`n" -ForegroundColor White

Write-Host "  4. Test the API (in another terminal):" -ForegroundColor Yellow
Write-Host "     curl http://localhost:5000/health`n" -ForegroundColor White

Write-Host "  5. For Docker deployment:" -ForegroundColor Yellow
Write-Host "     docker build -t power-theft-detector .`n" -ForegroundColor White
Write-Host "     docker run -p 5000:5000 power-theft-detector`n" -ForegroundColor White

Write-Host "See README.md and DEPLOYMENT_GUIDE.md for detailed instructions." -ForegroundColor Cyan
Write-Host "`n==========================================`n" -ForegroundColor Cyan
