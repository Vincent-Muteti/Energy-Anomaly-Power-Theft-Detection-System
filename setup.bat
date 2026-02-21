@echo off
REM Smart Power Disconnection Analytics System - Quick Start Script (Windows)
REM ========================================================================

echo ==========================================
echo Power Theft Detection System - Setup
echo ==========================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo Virtual environment activated

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
echo pip upgraded

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)
echo Dependencies installed

REM Verify installation
echo.
echo Running deployment verification tests...
echo ==========================================
python test_deployment.py
if errorlevel 1 (
    echo Error: Some tests failed
    exit /b 1
)

echo.
echo ==========================================
echo Setup complete!
echo.
echo Next steps:
echo   1. Activate virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Test the detector:
echo      python power_theft_detector.py
echo.
echo   3. Start the API server:
echo      python app.py
echo.
echo   4. Test the API (in another terminal):
echo      curl http://localhost:5000/health
echo.
echo   5. For Docker deployment:
echo      docker build -t power-theft-detector .
echo      docker run -p 5000:5000 power-theft-detector
echo.
echo See README.md and DEPLOYMENT_GUIDE.md for detailed instructions.
echo ==========================================
pause
