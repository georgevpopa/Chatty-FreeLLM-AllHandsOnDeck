"""
All Hands On Deck — FastAPI backend
- Fetches available NVIDIA NIM models dynamically
- Static task-based model recommendations
- Per-session usage tracking per provider
"""
import os
import subprocess
import httpx
import litellm
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

app = FastAPI(title="All Hands On Deck")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
litellm.drop_params = True

# Per-session usage counter
usage_counts = defaultdict(int)

CLOUD_PROVIDERS = {
    "nvidia":     {"key_env": "NVIDIA_NIM_API_KEY",  "prefix": "nvidia_nim", "rpm": 40},
    "groq":       {"key_env": "GROQ_API_KEY",        "prefix": "groq",       "rpm": 30},
    "cerebras":   {"key_env": "CEREBRAS_API_KEY",    "prefix": "cerebras",   "rpm": 30},
    "gemini":     {"key_env": "GEMINI_API_KEY",       "prefix": "gemini",     "rpm": 15},
    "mistral":    {"key_env": "MISTRAL_API_KEY",     "prefix": "mistral",    "rpm": 60},
    "openrouter": {"key_env": "OPENROUTER_API_KEY",  "prefix": "openrouter", "rpm": None},
}

# Static task → model recommendations
TASK_RECOMMENDATIONS = {
    "code":        {"model": "nvidia_nim/qwen/qwen2.5-coder-32b-instruct", "reason": "Specialized for code generation and review"},
    "logs":        {"model": "nvidia_nim/meta/llama-3.1-70b-instruct",     "reason": "Strong reasoning for log analysis"},
    "writing":     {"model": "nvidia_nim/mistralai/mistral-large-2-instruct", "reason": "Excellent prose and document generation"},
    "explain":     {"model": "nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b", "reason": "Best for deep technical explanations"},
    "fast":        {"model": "groq/llama-3.1-8b-instant",                  "reason": "Fastest response, good for quick questions"},
    "local":       {"model": "ollama/qwen2.5-coder:14b",                   "reason": "Private, no rate limits, runs on your machine"},
}


class ChatRequest(BaseModel):
    model: str
    message: str


class AiderRequest(BaseModel):
    model: str
    file_path: str
    instruction: str


@app.get("/")
async def index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/api/models")
async def get_models():
    models = {"local": [], "cloud": [], "nim_models": []}

    # Local Ollama models
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models["local"] = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass

    # Cloud providers status
    for name, cfg in CLOUD_PROVIDERS.items():
        if os.getenv(cfg["key_env"]):
            models["cloud"].append({"name": name, "rpm": cfg["rpm"]})

    # Fetch available NIM models if key is set
    nim_key = os.getenv("NVIDIA_NIM_API_KEY")
    if nim_key:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(
                    "https://integrate.api.nvidia.com/v1/models",
                    headers={"Authorization": f"Bearer {nim_key}"},
                )
                if r.status_code == 200:
                    models["nim_models"] = [m["id"] for m in r.json().get("data", [])]
        except Exception:
            pass

    return models


@app.get("/api/providers/status")
async def provider_status():
    status = {}
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            await client.get(f"{OLLAMA_URL}/api/tags")
        status["ollama"] = "online"
    except Exception:
        status["ollama"] = "offline"

    for name, cfg in CLOUD_PROVIDERS.items():
        status[name] = "configured" if os.getenv(cfg["key_env"]) else "no_key"

    return status


@app.get("/api/usage")
async def get_usage():
    return dict(usage_counts)


@app.get("/api/recommendations")
async def get_recommendations():
    return TASK_RECOMMENDATIONS


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        model = req.model
        if "/" not in model:
            model = f"ollama/{model}"

        kwargs = {"model": model, "messages": [{"role": "user", "content": req.message}]}

        if model.startswith("ollama/"):
            kwargs["api_base"] = OLLAMA_URL
        elif model.startswith("nvidia_nim/"):
            kwargs["api_key"] = os.getenv("NVIDIA_NIM_API_KEY")
        else:
            for cfg in CLOUD_PROVIDERS.values():
                if model.startswith(cfg["prefix"] + "/"):
                    kwargs["api_key"] = os.getenv(cfg["key_env"])
                    break

        response = await litellm.acompletion(**kwargs)

        # Track usage
        provider = model.split("/")[0]
        usage_counts[provider] += 1

        return {"reply": response.choices[0].message.content, "usage": dict(usage_counts)}

    except litellm.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit reached — switch provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/aider")
async def run_aider(req: AiderRequest):
    model = req.model
    if not model.startswith("ollama/"):
        model = f"ollama/{model}"

    cmd = ["aider", "--model", model, "--yes-always", "--no-pretty",
           "--message", req.instruction, req.file_path]
    env = {**os.environ, "OLLAMA_API_BASE": OLLAMA_URL}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
        return {"output": result.stdout, "errors": result.stderr}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="aider timed out")


app.mount("/static", StaticFiles(directory="static"), name="static")
