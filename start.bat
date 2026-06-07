@echo off
cd /d "%~dp0"

echo [INFO] Checking dependencies...
where uv >nul 2>&1 || (echo [ERROR] uv not found. Install: winget install astral-sh.uv && pause && exit /b 1)
where ollama >nul 2>&1 || echo [WARN] ollama not found - local models unavailable

echo [INFO] Installing dependencies...
uv sync -q

echo [INFO] Copying .env if missing...
if not exist .env copy .env.example .env >nul

echo [INFO] Starting litellm proxy on port 4000...
start "litellm-proxy" cmd /k "uv run litellm --config litellm_config.yaml --port 4000"

timeout /t 4 /nobreak >nul

echo [INFO] Starting web app on port 8000...
start "chatty-app" cmd /k "uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo.
echo =========================================
echo  chatty-local-claude is running!
echo  Open: http://localhost:8000
echo =========================================
echo.
start http://localhost:8000
pause
