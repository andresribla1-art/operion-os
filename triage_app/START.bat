@echo off
echo.
echo  OPERION TRIAGE - Clever Fit Ingolstadt
echo  ========================================
echo.

cd /d "%~dp0"

if not exist ".venv" (
    echo  Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo  Installing dependencies...
.venv\Scripts\pip.exe install -r requirements.txt -q

if not exist ".env" (
    echo.
    echo  ERROR: .env file not found.
    echo  Copy .env.example to .env and add your GROQ_API_KEY
    echo  Get a free key at: https://console.groq.com
    pause
    exit /b 1
)

for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="GROQ_API_KEY" set GROQ_API_KEY=%%b
)

echo.
echo  Starting server...
echo  Open browser: http://localhost:5000
echo  Press Ctrl+C to stop
echo.

.venv\Scripts\python.exe app.py
pause
