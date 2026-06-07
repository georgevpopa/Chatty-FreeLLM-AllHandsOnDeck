#!/usr/bin/env bash
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Incarca NVIDIA_NIM_API_KEY din .env
export $(grep -v '^#' "$SCRIPT_DIR/free-claude-code/.env" | xargs)

echo "[INFO] Pornire proxy pe portul 8082..."
cd "$SCRIPT_DIR/free-claude-code"
uv run uvicorn server:app --host 0.0.0.0 --port 8082
