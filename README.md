# 🤖 Chatty-FreeLLM-AllHandsOnDeck

> A local AI assistant with web interface that automatically rotates between free providers when rate limits are hit, and supports file editing through aider.

---

## 🎯 What It Does

- **Select a model** from the UI — local (Ollama) or free cloud
- **Chat** sends messages through litellm proxy to the selected model
- **If you hit rate limit** — the UI notifies you to select another provider
- **Aider tab** — provide a file path + instruction and the model edits the file autonomously
- **Live status** of all providers, refreshes every 30 seconds

---

## 🏗️ Architecture

```
Browser (http://localhost:8000)
        │
        ▼
  FastAPI app.py          ← serves UI + API
        │
        ▼
  litellm proxy :4000     ← routing, retry, rate limit tracking
        │
   ┌────┴──────────────────────┐
   ▼                           ▼
Ollama :11434           Cloud APIs (Groq, NVIDIA, etc.)
(local, unlimited)      (free, with rate limits)
```

---

## 📋 System Requirements

| Requirement | Details |
|---|---|
| OS | Windows 10/11 |
| Python | 3.10 – 3.12 (**not** 3.13/3.14) |
| RAM | 8GB minimum (16GB recommended) |
| uv | Python package manager |
| Ollama | for local models (optional) |

---

## 🟢 Step-by-Step Installation

### 1. Install uv

```powershell
winget install astral-sh.uv
```

Verify: `uv --version`

### 2. Install Ollama (for local models)

Download from: **https://ollama.com/download**

Configure model folder (if you want it on another drive):
```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\AI_Sandbox\models", "User")
```

Pull a model:
```powershell
ollama pull qwen2.5-coder:14b   # recommended — code + logs
ollama pull qwen2.5-coder:7b    # smaller — for 8GB RAM
```

### 3. Clone the repo

```powershell
git clone https://github.com/georgevpopa/Chatty-FreeLLM-AllHandsOnDeck.git
cd Chatty-FreeLLM-AllHandsOnDeck
```

### 4. Configure .env

```powershell
copy .env.example .env
notepad .env
```

Fill in the keys for the providers you want to use (all are optional):

```env
OLLAMA_BASE_URL=http://localhost:11434

NVIDIA_NIM_API_KEY=nvapi-...     # https://build.nvidia.com
GROQ_API_KEY=gsk_...             # https://console.groq.com
CEREBRAS_API_KEY=...             # https://cloud.cerebras.ai
GEMINI_API_KEY=...               # https://aistudio.google.com/apikey
MISTRAL_API_KEY=...              # https://console.mistral.ai
OPENROUTER_API_KEY=sk-or-...     # https://openrouter.ai/keys
```

### 5. Start the application

```powershell
start.bat
```

It automatically opens **http://localhost:8000** in your browser.

---

## 🚀 Usage

### Chat

1. Select a model from the sidebar (local or cloud)
2. Type your message in the input field
3. `Enter` sends, `Shift+Enter` for new line
4. If you see **⚠️ Rate limit** — select another provider from the sidebar

### Aider — File Editing

1. Click on the **🛠️ Aider** tab
2. Enter the full file path:
   ```
   C:\project\main.py
   ```
3. Enter the instruction:
   ```
   Fix all bugs and add proper error handling
   ```
4. Click **▶ Run Aider**
5. The result appears in the output field

---

## 🆓 Free Providers

| Provider | Available Models | Limit | Sign-up Link |
|---|---|---|---|
| **Ollama** (local) | qwen, llama, mistral, etc. | unlimited | https://ollama.com/library |
| **NVIDIA NIM** | llama-3.1-70b, nemotron, etc. | 40 req/min | https://build.nvidia.com |
| **Groq** | llama-3.1-70b, mixtral | 30 req/min | https://console.groq.com |
| **Cerebras** | llama3.1-70b | 30 req/min | https://cloud.cerebras.ai |
| **Gemini** | gemini-1.5-flash | 15 req/min | https://aistudio.google.com |
| **Mistral** | mistral-small | 1 req/sec | https://console.mistral.ai |
| **OpenRouter** | 50+ models :free | variable | https://openrouter.ai |

**Recommended strategy:** Ollama for repetitive tasks, Groq/NVIDIA for fast responses, Gemini/Mistral as fallback.

---

## 📦 Recommended Ollama Models

| Model | RAM | Best For |
|---|---|---|
| `qwen2.5-coder:7b` | ~6 GB | Machines with 8GB RAM |
| `qwen2.5-coder:14b` | ~10 GB | **Recommended** — code + log analysis |
| `qwen2.5:3b` | ~2 GB | Quick responses, limited RAM |
| `qwen3-coder:30b` | ~18 GB | Machines with 24+ GB RAM |

```powershell
# Download your desired model
ollama pull qwen2.5-coder:14b

# List installed models
ollama list
```

---

## ⌨️ Useful Commands

### Managing Ollama Models

```powershell
ollama list                          # installed models
ollama pull <model>                  # download model
ollama rm <model>                    # delete model
ollama run <model>                   # quick test in terminal
```

### Aider Directly in Terminal

```powershell
# Interactive mode
$env:OLLAMA_API_BASE="http://localhost:11434"
aider --model ollama/qwen2.5-coder:14b

# With specific file
aider --model ollama/qwen2.5-coder:14b "C:\path\to\file.py"

# Autonomous mode (no confirmation)
aider --model ollama/qwen2.5-coder:14b --yes-always --message "fix bugs" file.py
```

### Aider Commands

| Command | Description |
|---|---|
| `/add <file>` | Add file to context |
| `/drop <file>` | Remove file from context |
| `/clear` | Clear history |
| `/diff` | Show changes |
| `/undo` | Undo last change |
| `/exit` | Exit |

---

## ❌ FAQ & Common Issues

**App won't start**
→ Verify `uv` is installed: `uv --version`
→ Check that port 8000 isn't occupied: `netstat -ano | findstr :8000`

**Ollama not detected**
→ Verify Ollama is running (icon in system tray)
→ Test: `curl http://localhost:11434/api/tags`

**`model requires more system memory`**
→ Model is too large. Use `qwen2.5-coder:7b` or `qwen2.5:3b`

**Rate limit on cloud provider**
→ Normal — select another provider from the sidebar or use local Ollama

**Aider can't find the file**
→ Use the full path (e.g.: `C:\Users\georg\project\main.py`)
→ On WSL use format: `/mnt/c/Users/georg/project/main.py`

**litellm proxy won't start**
→ Verify `.env` exists and has at least `OLLAMA_BASE_URL` set
→ Run manually: `uv run litellm --config litellm_config.yaml --port 4000`

---

## 🗺️ Roadmap

- [x] litellm proxy with all free providers
- [x] FastAPI backend
- [x] Web UI with model selector + provider status
- [x] Aider integration for file editing
- [x] Windows startup script
- [ ] Automatic rate limit notification with switch to next provider
- [ ] Conversation history saved locally
- [ ] File upload directly from UI
- [ ] Log analysis support with pattern detection

---

## 🔒 Security

- All API keys stay in `.env` — **gitignored**, never uploaded to GitHub
- App runs only on `localhost` — not exposed to the network
- No conversation is sent anywhere except to the provider you selected

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=georgevpopa/Chatty-FreeLLM-AllHandsOnDeck&type=Date)](https://star-history.com/#georgevpopa/Chatty-FreeLLM-AllHandsOnDeck&Date)
