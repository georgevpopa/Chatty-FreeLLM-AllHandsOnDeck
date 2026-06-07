"""
chatty-local-claude — FastAPI backend
Handles: provider status, model list, chat proxy, aider bridge
"""
import os
import json
import subprocess
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="chatty-local-claude")
LITELLM_URL = f"http://localhost:{os.getenv('LITELLM_PROXY_PORT', 4000)}"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ─── Models ───────────────────────────────────────────────────────────────────

CLOUD_PROVIDERS = {
    "nvidia": {"key_env": "NVIDIA_NIM_API_KEY", "model": "cloud/nvidia-llama", "rpm": 40},
    "groq": {"key_env": "GROQ_API_KEY", "model": "cloud/groq-llama", "rpm": 30},
    "cerebras": {"key_env": "CEREBRAS_API_KEY", "model": "cloud/cerebras-llama", "rpm": 30},
    "gemini": {"key_env": "GEMINI_API_KEY", "model": "cloud/gemini-flash", "rpm": 15},
    "mistral": {"key_env": "MISTRAL_API_KEY", "model": "cloud/mistral-small", "rpm": 60},
    "openrouter": {"key_env": "OPENROUTER_API_KEY", "model": "cloud/openrouter-free", "rpm": None},
}


class ChatRequest(BaseModel):
    model: str
    message: str


class AiderRequest(BaseModel):
    model: str
    file_path: str
    instruction: str


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def index():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())


@app.get("/api/models")
async def get_models():
    """Returns local Ollama models + configured cloud providers."""
    models = {"local": [], "cloud": []}

    # Ollama local models
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models["local"] = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        models["local"] = []

    # Cloud providers — only show if API key is set
    for name, cfg in CLOUD_PROVIDERS.items():
        if os.getenv(cfg["key_env"]):
            models["cloud"].append({
                "name": name,
                "model": cfg["model"],
                "rpm": cfg["rpm"],
            })

    return models


@app.get("/api/providers/status")
async def provider_status():
    """Check which providers are reachable."""
    status = {}

    # Ollama
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            await client.get(f"{OLLAMA_URL}/api/tags")
        status["ollama"] = "online"
    except Exception:
        status["ollama"] = "offline"

    # Cloud providers
    for name, cfg in CLOUD_PROVIDERS.items():
        status[name] = "configured" if os.getenv(cfg["key_env"]) else "no_key"

    return status


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Proxy chat request to litellm."""
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{LITELLM_URL}/chat/completions",
                json={
                    "model": req.model,
                    "messages": [{"role": "user", "content": req.message}],
                },
            )
            r.raise_for_status()
            data = r.json()
            return {"reply": data["choices"][0]["message"]["content"]}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Rate limit reached — switch provider")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/aider")
async def run_aider(req: AiderRequest):
    """Run aider on a file with the selected model."""
    model = req.model
    # Map UI model name to aider format
    if not model.startswith("ollama/"):
        model = f"ollama/{model}"

    cmd = [
        "aider",
        "--model", model,
        "--yes-always",
        "--no-pretty",
        "--message", req.instruction,
        req.file_path,
    ]
    env = {**os.environ, "OLLAMA_API_BASE": OLLAMA_URL}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
        return {"output": result.stdout, "errors": result.stderr}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="aider timed out")


app.mount("/static", StaticFiles(directory="static"), name="static")
