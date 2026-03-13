# ✨ Prompt Refiner

> **Strip noise. Clarify intent. Get better outputs from any LLM.**

Prompt Refiner takes your raw, messy, assumption-filled prompts and transforms them into clean, structured, production-ready prompts — using Groq's free API for near-instant results.

---

## 📸 What it does

| Before | After |
|--------|-------|
| *"hey so i wanna build like a todo app in react idk maybe with drag and drop or something, can u write the code"* | *"Build a React todo application with drag-and-drop task reordering. Use React DnD or @dnd-kit. Include add, delete, and reorder functionality. Output the full component code with TypeScript."* |

**For every refinement you get:**
- ✅ Clean, structured prompt ready to paste into any LLM
- 📋 Change log — what was removed, clarified, restructured, or added
- 🎯 Intent summary — one-sentence description of what you actually want
- 📊 Quality score — 1–10 rating of the original prompt
- 🔍 Before / After comparison view

---

## 🗺️ Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                          User                               │
│                  types raw messy prompt                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                           │
│  ┌─────────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ input_panel.py  │  │ sidebar.py  │  │results_panel.py│  │
│  │ text area +     │  │ API key +   │  │ shows output + │  │
│  │ submit button   │  │ model pick  │  │ change log     │  │
│  └────────┬────────┘  └──────┬──────┘  └───────▲────────┘  │
└───────────┼─────────────────┼──────────────────┼───────────┘
            │                 │                  │
            └────────┬────────┘                  │ render
                     │                           │
                     ▼                           │
          ┌──────────────────────┐               │
          │       app.py         │               │
          │  orchestrates layout │               │
          │      + state         │               │
          └──────────┬───────────┘               │
                     │                           │
                     ▼                           │
          ┌──────────────────────┐               │
          │   core/refiner.py    │               │
          │  PromptRefiner class │ ──────────────┘
          │  + system prompt     │   RefinementResult
          └──────────┬───────────┘        │
                     │                    │
                     ▼                    ▼
          ┌──────────────────────┐  ┌─────────────────────┐
          │      Groq API        │  │   utils/history.py  │
          │  chat.completions    │  │   HistoryManager    │
          │  + JSON mode         │  │   session store     │
          └──────────┬───────────┘  └─────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │      LLM Model       │
          │  llama-3.3-70b  /    │
          │  mixtral / gemma2    │
          └──────────┬───────────┘
                     │
                     │  structured JSON response
                     │  {
                     │    refined_prompt,
                     │    changes [ ],
                     │    quality_score,
                     │    intent_summary
                     │  }
                     ▼
          ┌──────────────────────┐
          │   RefinementResult   │
          │     dataclass        │
          └──────────────────────┘
```

**Data flow summary:**

```
User prompt
  → input_panel.py       (captures text)
  → app.py               (passes to refiner)
  → core/refiner.py      (builds API request)
  → Groq API             (routes to LLM)
  → LLM                  (refines + returns JSON)
  → RefinementResult     (parsed dataclass)
  → results_panel.py     (renders to UI)
  → utils/history.py     (stores in session)
```

---

## 🏗️ Project structure

```
prompt_refiner/
├── app.py                      # Streamlit entry point & layout
├── requirements.txt
│
├── core/
│   └── refiner.py              # Groq API client, system prompt, dataclasses
│
├── components/
│   ├── input_panel.py          # Raw prompt text area + submit button
│   ├── results_panel.py        # Metrics, refined prompt, change log, diff view
│   └── sidebar.py              # API key input, model picker, history panel
│
└── utils/
    └── history.py              # In-session HistoryManager (up to 10 entries)
```

---

## ⚡ Quickstart

### 1. Clone & install

```bash
git clone https://github.com/yourname/prompt-refiner
cd prompt-refiner
pip install -r requirements.txt
```

### 2. Get a free Groq API key

1. Go to [console.groq.com](https://console.groq.com) — free, no credit card
2. **API Keys** → **Create API Key**
3. Copy the key (starts with `gsk_`)

### 3. Run

```bash
# Option A — environment variable (recommended)
export GROQ_API_KEY=gsk_...
streamlit run app.py

# Option B — enter key in the sidebar at runtime
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## 🤖 Available models

All free on Groq's tier:

| Model | Speed | Quality | Best for |
|-------|-------|---------|----------|
| `llama-3.3-70b-versatile` | Fast | ⭐⭐⭐⭐⭐ | Default — best results |
| `llama-3.1-8b-instant` | Fastest | ⭐⭐⭐ | Quick iteration |
| `mixtral-8x7b-32768` | Fast | ⭐⭐⭐⭐ | Structured JSON output |
| `gemma2-9b-it` | Fast | ⭐⭐⭐⭐ | Concise refinements |

---

## 🧩 Component breakdown

### `core/refiner.py`
The engine. Contains the system prompt, `PromptRefiner` class (wraps the Groq client), and `RefinementResult` / `Change` dataclasses. This is the only file that touches the API.

### `components/input_panel.py`
Renders the raw prompt `st.text_area` and the **Refine →** button. Returns `(prompt, submitted)` tuple to `app.py`.

### `components/results_panel.py`
Renders everything after a successful refinement — metrics row, intent summary, refined prompt code block, colour-coded change log, and the before/after expander.

### `components/sidebar.py`
Handles API key input, model selection, and the session history panel with clickable past refinements.

### `utils/history.py`
`HistoryManager` keeps the last 10 `RefinementResult` objects in Streamlit session state. Clicking a history entry reloads it into the results panel.

---

## 🔧 Extending

| Goal | Where to change |
|------|----------------|
| Swap LLM provider | `core/refiner.py` — replace Groq client |
| Persist history across sessions | `utils/history.py` — swap list for SQLite / JSON file |
| Export refined prompt as `.txt` | `components/results_panel.py` — add `st.download_button` |
| Batch refine from a file | `components/input_panel.py` — add `st.file_uploader` |
| Custom refinement rules | `core/refiner.py` — edit `SYSTEM_PROMPT` |

---

## 📦 Dependencies

```
groq>=0.9.0
streamlit>=1.35.0
```

---

## 📄 License

MIT