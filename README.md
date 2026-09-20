# OpsPilot — Context-to-Action Executive Agent

An autonomous workflow agent that transforms chaotic, unstructured communications (emails, meeting notes, Slack threads) into structured, dependency-aware execution plans with built-in uncertainty detection and human-in-the-loop approval.

![OpsPilot Demo](https://img.shields.io/badge/Status-Demo-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)

---

## ✨ Features

- **Unstructured Input Parsing** — Paste any chaotic email or meeting notes
- **Dependency Graph Extraction** — Automatically identifies task dependencies and sequential blockers
- **Uncertainty Flags** — Explicitly surfaces missing info (unassigned owners, ambiguous dates, conflicting schedules) instead of hallucinating
- **Source Grounding** — Every extracted task links back to the verbatim snippet from the original text
- **Confidence Scoring** — Each task carries a confidence score based on extraction certainty
- **Human-in-the-Loop Execution** — Review and approve before dispatching to external tools (Jira, Calendar, Slack)
- **Visual Execution Receipts** — Real-time feedback showing tool dispatch results and state changes

## 🏗️ Architecture

```
┌──────────────────┐       POST /api/analyze        ┌──────────────────────┐
│   index.html     │  ──────────────────────────►   │   backend.py         │
│   (Frontend)     │                                 │   (FastAPI Engine)   │
│                  │  ◄──────────────────────────    │                      │
│  • Input Box     │     PlanResponse JSON           │  • Task Extraction   │
│  • Uncertainty   │                                 │  • Uncertainty Flags │
│    Panel         │       POST /api/execute         │  • Dependency Graph  │
│  • Task Cards    │  ──────────────────────────►   │                      │
│  • Receipts      │  ◄──────────────────────────    │  • Tool Dispatch     │
│                  │     Execution Receipt            │    Simulation        │
└──────────────────┘                                 └──────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A modern web browser

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Backend

```bash
python backend.py
```

The API server starts at `http://127.0.0.1:8000`.

### 3. Open the Frontend

Double-click `index.html` or open it in your browser.

## 🎯 Demo Script (2.5 minutes)

| Time | Action | What to Highlight |
|------|--------|-------------------|
| 0:00 – 0:30 | Click **"Analyze & Reason Over Plan"** | Chaotic email → structured plan with 4 tasks |
| 0:30 – 1:15 | Point to the **Amber Uncertainty Banner** | Agent flagged missing owner, ambiguous time, date conflict — no hallucination |
| 1:15 – 1:45 | Click **"Inspect Source"** on TSK-101 | Verbatim source grounding in the left panel |
| 1:45 – 2:30 | Click **"Approve & Dispatch →"** on TSK-101 | Execution receipt: `PAYTM-402`, state change visible |

## 📁 Project Structure

```
ops-pilot-demo/
├── backend.py       # FastAPI server with /analyze and /execute endpoints
├── index.html       # Single-file frontend (Tailwind CSS + Font Awesome)
├── requirements.txt # Python dependencies
├── .gitignore       # Git ignore rules
└── README.md        # This file
```

## 🔌 API Endpoints

### `POST /api/analyze`

Accepts unstructured text and returns a structured execution plan.

**Request:**
```json
{
  "text": "Hey everyone, quick update from today's call..."
}
```

**Response:** `PlanResponse` containing:
- `summary` — High-level plan description
- `uncertainties[]` — Flagged missing/ambiguous information
- `tasks[]` — Executable task items with dependencies, confidence scores, and tool targets

### `POST /api/execute`

Dispatches a task to an external tool (simulated).

**Request:**
```json
{
  "task_id": "TSK-101",
  "tool": "JIRA",
  "payload": {}
}
```

**Response:** Execution receipt with status, receipt ID, and state change description.

## 🛠️ Extending

In production, replace the deterministic response in `analyze_document()` with an LLM call (e.g., Gemini, GPT-4) using structured output schemas to extract tasks from arbitrary text.

## 📄 License

MIT
