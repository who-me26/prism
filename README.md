# ⚡ PRISM — AI-Powered Research Assistant

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini AI](https://img.shields.io/badge/Google%20GenAI-Gemini%202.5-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com/)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B.svg)](https://arxiv.org/)
[![Wikipedia API](https://img.shields.io/badge/Wikipedia-API-white.svg?logo=wikipedia&logoColor=black)](https://www.wikipedia.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **PRISM** (Predictive & Research Intelligence Synthesis Model) is an elite, multi-source AI research assistant built with **Python**, **Streamlit**, and **Google Gemini AI**. It bridges the gap between scientific literature, encyclopedic domain knowledge, and real-time environmental context through an intelligent tool routing architecture.

---

## 🌟 Highlights & Project Overview

* **Intelligent Gemini AI Integration**: Designed and developed an AI-powered research assistant using Streamlit, integrating Gemini AI (`gemini-2.5-flash`, `gemini-1.5-pro`) for intelligent, context-aware responses and multi-source synthesis.
* **Multi-Source Information Retrieval**: Integrated **Wikipedia search**, the **arXiv API** for research paper and preprint discovery, and a **live Weather API** (Open-Meteo & wttr.in) to support fast, multi-source information retrieval with live citations and direct PDF downloads.
* **Intelligent Tool Routing Engine**: Built an intuitive, modern UI featuring a dual-layer tool routing engine (AI-based semantic router with heuristic fallback) that automatically classifies user intent, determines which data providers to query, improves user productivity, and eliminates manual searching across disparate sources.
* **Interactive Research Dossier**: Auto-archives research sessions and generates downloadable Markdown dossiers compiling executive summaries, paper citations, and encyclopedic overviews.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────┐
                                  │      User Query Input     │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │    ⚡ Intelligent Tool Routing Engine         │
                         │   (Gemini Semantic Intent / Rule Fallback)   │
                         └──────┬───────────────┬──────────────┬────────┘
                                │               │              │
                     ┌──────────┴──────┐ ┌──────┴─────────┐ ┌──┴─────────────┐
                     │  arXiv Paper API│ │ Wikipedia API  │ │ Live Weather API│
                     │ (2M+ Preprints) │ │ (Encyclopedia) │ │  (Open-Meteo)   │
                     └──────────┬──────┘ └──────┬─────────┘ └──┬─────────────┘
                                │               │              │
                                └───────────────┼──────────────┘
                                                │
                                                ▼
                               ┌────────────────────────────────┐
                               │     Gemini AI Synthesis Core   │
                               │  - Cross-Source Reasoning      │
                               │  - Academic Citation Mapping   │
                               │  - Executive Briefing Gen      │
                               └────────────────┬───────────────┘
                                                │
                                                ▼
                               ┌────────────────────────────────┐
                               │  Streamlit Modern Interface    │
                               │  (Interactive Cards & Dossier) │
                               └────────────────────────────────┘
```

---

## ✨ Core Features

### 1. 🧠 Smart Assistant & Auto-Routing
- Automatically detects inquiry intent (academic paper request, historical/concept definition, meteorological observation, or multi-domain synthesis).
- Displays visual routing badges and transparent reasoning strategies for every decision.
- Executes tools in parallel and generates a structured research briefing with executive summary, academic methodology breakdown, and citations.

### 2. 📚 arXiv Academic Paper Discovery
- Search millions of peer-reviewed papers and preprints on arXiv.
- Sort by **Relevance**, **Submission Date**, or **Last Updated Date**.
- Direct links to read papers and one-click PDF downloads.

### 3. 🌐 Wikipedia Knowledge Explorer
- Fast encyclopedic search with configurable summary depth.
- Extracted section headers, disambiguation resolution, and canonical reference links.

### 4. ⛅ Live Global Weather Station
- Instant real-time atmospheric observations (temperature, feels-like, humidity, wind speed, condition emojis).
- 5-day daily forecast outlook.
- Metric (°C) and Imperial (°F) unit toggles.

### 5. 📑 Research Dossier & Export
- Persistent session state tracking all queries, findings, and tool executions.
- Single-click export to a downloadable, professionally formatted Markdown dossier (`.md`).

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10 or higher
- A free Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey) *(optional for basic search; required for AI synthesis)*

### 1. Clone the Repository
```bash
git clone https://github.com/who-me26/prism.git
cd prism
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the `prism` root folder:
```bash
copy .env.example .env
```
Add your key inside `.env`:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(Alternatively, enter your API key directly in the Streamlit web sidebar during runtime).*

### 4. Run the Application
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 📁 Repository Structure

```
prism/
├── .streamlit/
│   └── config.toml          # Custom dark modern UI theme
├── components/
│   ├── __init__.py
│   ├── history.py           # Session management & dossier exporter
│   └── ui.py                # Custom CSS styling, hero, & badge widgets
├── tools/
│   ├── __init__.py
│   ├── arxiv_tool.py        # arXiv preprint discovery API
│   ├── gemini_client.py     # Google GenAI SDK v2 & synthesis engine
│   ├── router.py            # Intelligent tool routing engine
│   ├── weather_tool.py      # Real-time Open-Meteo & wttr.in weather API
│   └── wiki_tool.py         # Wikipedia encyclopedia API
├── .env.example             # Template for API credentials
├── .gitignore               # Ignored files (secrets, caches, venv)
├── app.py                   # Main Streamlit web application
├── README.md                # Project documentation
└── requirements.txt         # Production dependencies
```

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend & UI** | [Streamlit](https://streamlit.io/) | Modern reactive web UI with custom glassmorphic CSS |
| **Language Model** | [Google Gemini AI](https://ai.google.dev/) | `gemini-2.5-flash` / `gemini-1.5-pro` via `google-genai` SDK v2 |
| **Academic Search** | [arXiv API](https://arxiv.org/) | Preprints, abstracts, author details, and PDF retrieval |
| **Encyclopedia** | [Wikipedia API](https://pypi.org/project/wikipedia/) | Verified global encyclopedic context and summaries |
| **Meteorology** | [Open-Meteo](https://open-meteo.com/) | Live weather conditions, temperatures, and 5-day forecasts |
| **Language** | Python 3.10+ | Core language |

---

## 📜 License
This project is open-source and licensed under the [MIT License](LICENSE).
