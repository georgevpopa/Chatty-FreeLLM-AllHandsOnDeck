@echo off
for /f "delims=" %%i in ('wsl wslpath -u "%~dp0."') do set WSL_DIR=%%i
for /f %%u in ('wsl whoami') do set WSL_USER=%%u

echo [INFO] Instalare uv daca lipseste...
wsl bash -c "command -v uv &>/dev/null || curl -Ls https://astral.sh/uv/install.sh | sh"

echo [INFO] Clone + sync dependinte...
wsl bash --noprofile --norc -c "export PATH=/home/%WSL_USER%/.local/bin:/usr/local/bin:/usr/bin:/bin; cd \"%WSL_DIR%\" && [ ! -d free-claude-code ] && git clone https://github.com/Alishahryar1/free-claude-code; cd free-claude-code && [ ! -f .env ] && cp .env.example .env; uv sync -q"

echo [INFO] Pornire proxy in fereastra noua...
start cmd /k wsl bash "%WSL_DIR%/start-proxy.sh"

echo [INFO] Astept 6 secunde...
timeout /t 6 /nobreak >nul

echo [INFO] Lansare Claude...
start cmd /k wsl bash --noprofile --norc -c "export PATH=/home/%WSL_USER%/.local/bin:/usr/local/bin:/usr/bin:/bin; export ANTHROPIC_BASE_URL=http://localhost:8082; claude"

echo [OK] Gata.
pause
