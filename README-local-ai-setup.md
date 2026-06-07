# 🤖 Local AI Agent Setup — Windows + Ollama + Aider

Setup complet pentru un coding assistant AI local, privat, fără costuri, care rulează pe mașina ta.

---

## 🎯 Ce obții la final

- **Ollama** — server local de modele LLM
- **aider** — coding assistant în terminal (cod, analiză loguri, debug)
- **100% local** — nicio dată nu pleacă din mașina ta
- **Fără costuri** — niciun API key, niciun abonament

---

## 📋 Cerințe sistem

| Cerință | Minim | Recomandat |
|---|---|---|
| OS | Windows 10/11 | Windows 11 |
| RAM | 8 GB | 16+ GB |
| Spațiu disk | 10 GB | 50+ GB (pentru modele mari) |
| Python | 3.10–3.12 | 3.12 |

---

## 🟢 Pasul 1 — Instalează Ollama

Descarcă și instalează de la: **https://ollama.com/download**

Verifică instalarea:
```powershell
ollama --version
```

### Configurare folder modele (opțional, recomandat)

Dacă vrei modelele pe un alt drive (ex: `E:\AI_Sandbox\models`):
```powershell
[System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\AI_Sandbox\models", "User")
```

Repornește Ollama după setare (click dreapta system tray → Quit → redeschide).

---

## 🟢 Pasul 2 — Alege și descarcă un model

Alege în funcție de RAM-ul disponibil:

| Model | RAM necesar | Calitate | Ideal pentru |
|---|---|---|---|
| `qwen2.5-coder:7b` | ~6 GB | ⭐⭐⭐ | Mașini cu 8GB RAM |
| `qwen2.5-coder:14b` | ~10 GB | ⭐⭐⭐⭐ | **Recomandat** — cod + loguri |
| `qwen3-coder:30b` | ~18 GB | ⭐⭐⭐⭐⭐ | Mașini cu 24+ GB RAM |

**Link-uri modele:**
- https://ollama.com/library/qwen2.5-coder
- https://ollama.com/library/qwen3-coder
- https://ollama.com/library/qwen2.5 (general purpose)

```powershell
# Descarcă modelul ales (ex: 14b)
ollama pull qwen2.5-coder:14b
```

Verifică modele instalate:
```powershell
ollama list
```

---

## 🟢 Pasul 3 — Instalează uv (Python package manager)

```powershell
winget install astral-sh.uv
```

Verifică:
```powershell
uv --version
```

---

## 🟢 Pasul 4 — Instalează aider

```powershell
uv tool install aider-chat --python 3.12
```

Verifică:
```powershell
aider --version
```

---

## 🚀 Utilizare

### Pornire simplă

```powershell
$env:OLLAMA_API_BASE="http://localhost:11434"
aider --model ollama/qwen2.5-coder:14b
```

### Analiză fișier specific

```powershell
# La pornire
aider --model ollama/qwen2.5-coder:14b "C:\path\to\file.log"

# Din interiorul aider
/add C:\path\to\file.log
```

### Mod autonom (aprobă toate modificările automat)

```powershell
aider --model ollama/qwen2.5-coder:14b --yes-always --message "fix all bugs in main.py"
```

### Comenzi utile în aider

| Comandă | Descriere |
|---|---|
| `/add <file>` | Adaugă fișier în context |
| `/drop <file>` | Scoate fișier din context |
| `/clear` | Șterge istoricul conversației |
| `/diff` | Arată modificările făcute |
| `/undo` | Anulează ultima modificare |
| `/exit` | Ieșire |

---

## ❌ Probleme frecvente

**`model requires more system memory`**
→ Modelul e prea mare pentru RAM disponibil. Folosește un model mai mic sau închide alte aplicații.

**`OllamaException: connection refused`**
→ Ollama nu rulează. Pornește-l: `ollama serve`

**`aider: command not found`**
→ Repornește terminalul după instalare sau rulează: `uv tool install aider-chat --python 3.12`

**`No module named 'pkg_resources'`**
→ Problemă de compatibilitate Python. Asigură-te că folosești Python 3.12: `uv tool install aider-chat --python 3.12`

---

## 🗺️ Roadmap personal

- [x] Ollama instalat și configurat
- [x] Modele descărcate în `E:\AI_Sandbox\models`
- [x] aider funcțional cu `qwen2.5-coder:14b`
- [ ] Workflow pentru analiză loguri de rețea
- [ ] Integrare cu proiectul OneNote FAQ RAG Agent

---

## 🔗 Link-uri utile

| Resursă | Link |
|---|---|
| Ollama | https://ollama.com |
| Ollama modele | https://ollama.com/library |
| aider documentație | https://aider.chat |
| aider comenzi | https://aider.chat/docs/usage/commands.html |
| uv (Python) | https://docs.astral.sh/uv |
| qwen2.5-coder | https://ollama.com/library/qwen2.5-coder |
| qwen3-coder | https://ollama.com/library/qwen3-coder |
