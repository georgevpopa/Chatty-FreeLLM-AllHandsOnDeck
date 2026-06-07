#!/usr/bin/env bash
# setup-free-claude-code.sh
# Clonează, configurează și pornește proxy-ul free-claude-code
# Utilizare: bash setup-free-claude-code.sh

set -euo pipefail

# ─── Validare dependințe ──────────────────────────────────────────────────────

if ! command -v uv &>/dev/null; then
    echo "[ERROR] Utilitarul 'uv' nu este instalat."
    echo "        Instalează-l cu: curl -Ls https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command -v docker &>/dev/null; then
    echo "[ERROR] Docker runtime nu este disponibil în PATH."
    echo "        Asigură-te că Docker Desktop este instalat și pornit."
    exit 1
fi

if ! docker info &>/dev/null; then
    echo "[ERROR] Docker daemon nu rulează sau nu ai permisiuni (fără root necesar, dar user trebuie în grupul 'docker')."
    echo "        Rulează: sudo usermod -aG docker \$USER  apoi reloghează-te."
    exit 1
fi

echo "[OK] Dependințe validate: uv și Docker sunt disponibile."

# ─── 1. Clonare repository ────────────────────────────────────────────────────

REPO_URL="https://github.com/Alishahryar1/free-claude-code"
REPO_DIR="free-claude-code"

if [ -d "$REPO_DIR" ]; then
    echo "[INFO] Directorul '$REPO_DIR' există deja, se sare clonarea."
else
    echo "[INFO] Clonare repository..."
    git clone "$REPO_URL"
fi

cd "$REPO_DIR"

# ─── 2. Inițializare dependințe Python cu uv ─────────────────────────────────

echo "[INFO] Inițializare mediu virtual și dependințe cu uv..."
uv sync

# ─── 3. Configurare fișier .env ──────────────────────────────────────────────

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo "[INFO] Fișierul .env.example a fost copiat în .env"
    else
        touch ".env"
        echo "[INFO] Fișierul .env.example nu există, s-a creat .env gol."
    fi
else
    echo "[INFO] Fișierul .env există deja, se păstrează."
fi

# Adaugă NVIDIA_NIM_API_KEY dacă nu există deja în .env
if ! grep -q "NVIDIA_NIM_API_KEY" ".env"; then
    cat >> ".env" <<'EOF'

# NVIDIA NIM API Key
# Generează un token gratuit (40 req/min) de pe: https://build.nvidia.com
# Creează cont, selectează un model, click "Get API Key" și copiază token-ul aici.
NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key_here
EOF
    echo "[INFO] Placeholder NVIDIA_NIM_API_KEY adăugat în .env"
else
    echo "[INFO] NVIDIA_NIM_API_KEY există deja în .env, se păstrează valoarea curentă."
fi

# ─── 4. Pornire server proxy în background ────────────────────────────────────

LOG_FILE="/tmp/free-claude-code-proxy.log"

echo "[INFO] Pornire server proxy pe portul 8082 (background)..."
nohup uv run uvicorn server:app --host 0.0.0.0 --port 8082 > "$LOG_FILE" 2>&1 &
PROXY_PID=$!

echo "[OK] Server proxy pornit cu PID=$PROXY_PID"
echo "     Log-uri disponibile la: $LOG_FILE"

# Așteaptă câteva secunde pentru ca serverul să pornească
sleep 3

if ! kill -0 "$PROXY_PID" 2>/dev/null; then
    echo "[ERROR] Serverul proxy nu a pornit corect. Verifică log-urile: $LOG_FILE"
    exit 1
fi

echo "[OK] Serverul proxy rulează."

# ─── 5. Export variabilă de mediu și lansare claude ──────────────────────────

export ANTHROPIC_BASE_URL="http://localhost:8082"
echo "[OK] ANTHROPIC_BASE_URL exportat: $ANTHROPIC_BASE_URL"

echo ""
echo "─────────────────────────────────────────────────────────"
echo "  Setup complet! Se lansează clientul claude..."
echo "  (Pentru a opri proxy-ul: kill $PROXY_PID)"
echo "─────────────────────────────────────────────────────────"
echo ""

claude
