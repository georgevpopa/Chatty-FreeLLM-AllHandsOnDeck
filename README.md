# 🤖 chatty-local-claude

> Un AI assistant local cu interfață web, care rotește automat între provideri gratuiți când se atinge limita de rate, și suportă editare de fișiere prin aider.

---

## 🎯 Ce face

- **Selectezi modelul** din UI — local (Ollama) sau cloud gratuit
- **Chatul** trimite mesajele prin litellm proxy la modelul selectat
- **Dacă dai rate limit** — UI-ul te anunță și selectezi alt provider
- **Tab Aider** — dai o cale de fișier + instrucțiune și modelul editează fișierul autonom
- **Status live** al tuturor providerilor, refresh la 30 secunde

---

## 🏗️ Arhitectură

```
Browser (http://localhost:8000)
        │
        ▼
  FastAPI app.py          ← servește UI + API
        │
        ▼
  litellm proxy :4000     ← rutare, retry, rate limit tracking
        │
   ┌────┴──────────────────────┐
   ▼                           ▼
Ollama :11434           Cloud APIs (Groq, NVIDIA, etc.)
(local, nelimitat)      (gratuite, cu rate limits)
```

---

## 📋 Cerințe sistem

| Cerință | Detalii |
|---|---|
| OS | Windows 10/11 |
| Python | 3.10 – 3.12 (**nu** 3.13/3.14) |
| RAM | 8GB minim (16GB recomandat) |
| uv | package manager Python |
| Ollama | pentru modele locale (opțional) |

---

## 🟢 Instalare pas cu pas

### 1. Instalează uv

```powershell
winget install astral-sh.uv
```

Verifică: `uv --version`

### 2. Instalează Ollama (pentru modele locale)

Descarcă de la: **https://ollama.com/download**

Configurează folderul de modele (dacă vrei pe alt drive):
```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\AI_Sandbox\models", "User")
```

Trage un model:
```powershell
ollama pull qwen2.5-coder:14b   # recomandat — cod + loguri
ollama pull qwen2.5-coder:7b    # mai mic — pentru 8GB RAM
```

### 3. Clonează repo-ul

```powershell
git clone https://github.com/georgevpopa/chatty-local-claude.git
cd chatty-local-claude
```

### 4. Configurează .env

```powershell
copy .env.example .env
notepad .env
```

Completează cheile pentru providerii pe care vrei să îi folosești (toate sunt opționale):

```env
OLLAMA_BASE_URL=http://localhost:11434

NVIDIA_NIM_API_KEY=nvapi-...     # https://build.nvidia.com
GROQ_API_KEY=gsk_...             # https://console.groq.com
CEREBRAS_API_KEY=...             # https://cloud.cerebras.ai
GEMINI_API_KEY=...               # https://aistudio.google.com/apikey
MISTRAL_API_KEY=...              # https://console.mistral.ai
OPENROUTER_API_KEY=sk-or-...     # https://openrouter.ai/keys
```

### 5. Pornește aplicația

```powershell
start.bat
```

Se deschide automat **http://localhost:8000** în browser.

---

## 🚀 Utilizare

### Chat

1. Selectează un model din sidebar (local sau cloud)
2. Scrie mesajul în câmpul de jos
3. `Enter` trimite, `Shift+Enter` linie nouă
4. Dacă apare **⚠️ Rate limit** — selectează alt provider din sidebar

### Aider — editare fișiere

1. Click pe tab-ul **🛠️ Aider**
2. Introdu calea completă a fișierului:
   ```
   C:\proiect\main.py
   ```
3. Introdu instrucțiunea:
   ```
   Fix all bugs and add proper error handling
   ```
4. Click **▶ Run Aider**
5. Rezultatul apare în câmpul de output

---

## 🆓 Provideri gratuiți

| Provider | Modele disponibile | Limită | Link înregistrare |
|---|---|---|---|
| **Ollama** (local) | qwen, llama, mistral, etc. | nelimitat | https://ollama.com/library |
| **NVIDIA NIM** | llama-3.1-70b, nemotron, etc. | 40 req/min | https://build.nvidia.com |
| **Groq** | llama-3.1-70b, mixtral | 30 req/min | https://console.groq.com |
| **Cerebras** | llama3.1-70b | 30 req/min | https://cloud.cerebras.ai |
| **Gemini** | gemini-1.5-flash | 15 req/min | https://aistudio.google.com |
| **Mistral** | mistral-small | 1 req/sec | https://console.mistral.ai |
| **OpenRouter** | 50+ modele :free | variabil | https://openrouter.ai |

**Strategie recomandată:** Ollama pentru taskuri repetitive, Groq/NVIDIA pentru răspunsuri rapide, Gemini/Mistral ca fallback.

---

## 📦 Modele Ollama recomandate

| Model | RAM | Ideal pentru |
|---|---|---|
| `qwen2.5-coder:7b` | ~6 GB | Mașini cu 8GB RAM |
| `qwen2.5-coder:14b` | ~10 GB | **Recomandat** — cod + analiză loguri |
| `qwen2.5:3b` | ~2 GB | Răspunsuri rapide, RAM limitat |
| `qwen3-coder:30b` | ~18 GB | Mașini cu 24+ GB RAM |

```powershell
# Descarcă modelul dorit
ollama pull qwen2.5-coder:14b

# Listează modelele instalate
ollama list
```

---

## ⌨️ Comenzi utile

### Gestionare modele Ollama

```powershell
ollama list                          # modele instalate
ollama pull <model>                  # descarcă model
ollama rm <model>                    # șterge model
ollama run <model>                   # test rapid în terminal
```

### Aider direct în terminal

```powershell
# Pornire interactivă
$env:OLLAMA_API_BASE="http://localhost:11434"
aider --model ollama/qwen2.5-coder:14b

# Cu fișier specific
aider --model ollama/qwen2.5-coder:14b "C:\path\to\file.py"

# Mod autonom (fără confirmare)
aider --model ollama/qwen2.5-coder:14b --yes-always --message "fix bugs" file.py
```

### Comenzi în aider

| Comandă | Descriere |
|---|---|
| `/add <file>` | Adaugă fișier în context |
| `/drop <file>` | Scoate fișier din context |
| `/clear` | Șterge istoricul |
| `/diff` | Arată modificările |
| `/undo` | Anulează ultima modificare |
| `/exit` | Ieșire |

---

## ❌ FAQ & Probleme frecvente

**App-ul nu pornește**
→ Verifică că `uv` e instalat: `uv --version`
→ Verifică că portul 8000 nu e ocupat: `netstat -ano | findstr :8000`

**Ollama nu e detectat**
→ Verifică că Ollama rulează (iconița în system tray)
→ Testează: `curl http://localhost:11434/api/tags`

**`model requires more system memory`**
→ Modelul e prea mare. Folosește `qwen2.5-coder:7b` sau `qwen2.5:3b`

**Rate limit la provider cloud**
→ Normal — selectează alt provider din sidebar sau folosește Ollama local

**Aider nu găsește fișierul**
→ Folosește calea completă (ex: `C:\Users\georg\proiect\main.py`)
→ Pe WSL folosește format: `/mnt/c/Users/georg/proiect/main.py`

**litellm proxy nu pornește**
→ Verifică că `.env` există și are cel puțin `OLLAMA_BASE_URL` setat
→ Rulează manual: `uv run litellm --config litellm_config.yaml --port 4000`

---

## 🗺️ Roadmap

- [x] litellm proxy cu toți providerii gratuiți
- [x] FastAPI backend
- [x] Web UI cu selector model + status provideri
- [x] Integrare aider pentru editare fișiere
- [x] Startup script Windows
- [ ] Notificare automată rate limit cu switch la next provider
- [ ] Istoric conversații salvat local
- [ ] Upload fișier direct din UI
- [ ] Suport pentru analiză loguri cu pattern detection

---

## 🔒 Securitate

- Toate cheile API stau în `.env` — **gitignored**, nu se urcă pe GitHub
- App-ul rulează doar pe `localhost` — nu e expus în rețea
- Nicio conversație nu e trimisă nicăieri în afara providerului selectat de tine


---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=georgevpopa/Chatty-FreeLLM-AllHandsOnDeck&type=Date)](https://star-history.com/#georgevpopa/Chatty-FreeLLM-AllHandsOnDeck&Date)

