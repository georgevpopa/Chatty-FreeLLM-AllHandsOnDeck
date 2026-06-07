@echo off
title All Hands On Deck
cd /d "%~dp0"

echo ==========================================
echo   All Hands On Deck - Starting...
echo ==========================================
echo.

:: Check uv
where uv >nul 2>&1 || (
    echo [ERROR] uv not found. Install with: winget install astral-sh.uv
    pause & exit /b 1
)

:: Install/update dependencies silently
echo [1/4] Checking dependencies...
uv sync -q

:: Copy .env if missing
if not exist .env (
    copy .env.example .env >nul
    echo [INFO] Created .env from template - edit it to add API keys
)

:: Start Ollama if not running
echo [2/4] Checking Ollama...
curl -s --max-time 2 http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% neq 0 (
    where ollama >nul 2>&1
    if %ERRORLEVEL% eq 0 (
        echo [INFO] Starting Ollama...
        start "" ollama serve
        :: Wait for Ollama to be ready
        for /l %%i in (1,1,10) do (
            timeout /t 1 /nobreak >nul
            curl -s --max-time 1 http://localhost:11434/api/tags >nul 2>&1
            if not errorlevel 1 goto ollama_ready
        )
        echo [WARN] Ollama started but not responding yet
    ) else (
        echo [WARN] Ollama not installed - local models unavailable
    )
) else (
    echo [OK] Ollama already running
)
:ollama_ready

:: Kill any existing instance on port 8000
echo [3/4] Checking port 8000...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8000 "') do (
    taskkill /f /pid %%p >nul 2>&1
)

:: Start the app
echo [4/4] Starting web app...
start "All Hands On Deck" /min cmd /k "cd /d %~dp0 && uv run uvicorn app:app --host 0.0.0.0 --port 8000"

:: Wait for app to be ready
echo.
echo Waiting for app to start...
for /l %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    curl -s --max-time 1 http://localhost:8000 >nul 2>&1
    if not errorlevel 1 goto app_ready
)
echo [WARN] App may still be starting...

:app_ready
echo.
echo ==========================================
echo   Running at: http://localhost:8000
echo ==========================================
echo.
start http://localhost:8000
exit
