@echo off
echo ========================================
echo   NextLeap Chatbot - Starting Services
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Installing backend dependencies...
cd backend
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo [2/3] Starting FastAPI backend server...
start "NextLeap Backend" cmd /k "python server.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo [3/3] Opening chatbot UI in browser...
cd ..\frontend
start "" "index.html"

echo.
echo ========================================
echo   Services Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: Opening in browser...
echo.
echo Press any key to stop the backend server...
pause >nul

REM Kill the backend server
taskkill /FI "WindowTitle eq NextLeap Backend*" /T /F >nul 2>&1
echo Backend server stopped.
