

---

```markdown
# OpsPilot: Context-to-Action Executive Agent

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-8E75C2?style=flat&logo=googlegemini&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)
![Status](https://img.shields.io/badge/Status-Hackathon_Prototype-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **Turn messy workplace communication into approved, verifiable execution plans.**

OpsPilot transforms chaotic communication (emails, meeting transcripts, Slack threads) into a dependency-aware execution graph, then dispatches external actions only after explicit human approval.

Instead of generating passive summaries, OpsPilot identifies deliverables, responsible owners, deadlines, blockers, and ambiguities—flagging missing context rather than hallucinating facts.

---

### Dashboard Preview

![OpsPilot Interface](https://github.com/user-attachments/assets/7e39849d-a168-4e54-9513-ccd4fa7305ff)

---

## Core Capabilities


```

Unstructured Input ──► Reasoning & Extraction ──► Uncertainty Check ──► Dependency Graph ──► Human-in-the-Loop ──► Tool Receipt

```

* **Deterministic Structured Extraction:** Uses the Gemini API with schema enforcement to parse tasks, assignees, deadlines, and priorities directly into typed entities.
* **Explicit Uncertainty Detection:** Prevents hallucinated planning. Missing DRIs, unstated times, or date conflicts surface as dedicated warning banners with concrete recovery actions.
* **Verifiable Source Grounding:** Every extracted item indexes the exact snippet from the raw source text for fast verification.
* **Dependency-Aware Ordering:** Reconstructs explicit blocker chains (e.g., `Patch DB` $\rightarrow$ `QA Verification` $\rightarrow$ `Release Freeze Review` $\rightarrow$ `Canary Deployment`).
* **Zero-Trust Human-in-the-Loop (HITL):** Decouples reasoning from mutation. Sensitive external side-effects require human verification.
* **Auditable Tool Receipts:** Dispatches to target tool handlers (Jira, Google Calendar, Slack) and returns auditable state updates.

---

## Architecture

```text
       ┌───────────────────────────────┐
       │   index.html (Client App)     │
       │   Tailwind CSS + Vanilla JS   │
       └──────────────┬────────────────┘
                      │
                      │  POST /api/analyze { text }
                      ▼
       ┌───────────────────────────────┐
       │     backend.py (FastAPI)      │
       ├───────────────────────────────┤
       │ 1. Gemini Structured Engine   │──► PlanResponse (Schema Enforced)
       │ 2. Offline Fallback Guard     │──► Deterministic Scenario (Wi-Fi proof)
       └──────────────┬────────────────┘
                      │
                      │  Human Review & Approval in UI
                      ▼
       ┌───────────────────────────────┐
       │     POST /api/execute         │
       ├───────────────────────────────┤
       │ 3. Simulated Tool Dispatchers │──► Jira Service Desk (PAYTM-XXX)
       │    (Receipt Engine)           │──► Google Calendar Event
       │                               │──► Slack Alert Broadcaster
       └───────────────────────────────┘

```

### Network-Resilient Offline Fallback

To ensure smooth demonstrations during unstable network conditions or rate limits, `/api/analyze` includes an automatic failover guard. If `GEMINI_API_KEY` is not present or an upstream connection fails, the backend switches to a cached production scenario to keep UI execution uninterrupted.

---

## API Specification

### `POST /api/analyze`

Extracts tasks, dependencies, and uncertainties from raw text.

* **Request:**
```json
{
  "text": "DevOps should fix the connection pool issue before Thursday..."
}

```


* **Response (`PlanResponse`):**
```json
{
  "summary": "Sprint alignment on DB connection pool fix and Friday release freeze.",
  "uncertainties": [
    {
      "id": "UNC-1",
      "field": "DB Failover Ownership",
      "issue": "DevOps mentioned generally, but specific DRI is not assigned.",
      "recommended_action": "Block execution until owner is confirmed."
    }
  ],
  "tasks": [
    {
      "id": "TSK-101",
      "title": "Patch DB Connection Pool",
      "assignee": "DevOps Team",
      "assignee_status": "UNCONFIRMED",
      "deadline": "Thursday EOD",
      "deadline_status": "CONFIRMED",
      "priority": "HIGH",
      "grounded_snippet": "We should probably get the connection pool issue fixed before Thursday.",
      "confidence": 0.94,
      "dependencies": [],
      "tool_target": "JIRA",
      "execution_payload": {
        "project": "PAYTM",
        "issue_type": "Bug Fix",
        "priority": "High"
      },
      "status": "PENDING_APPROVAL"
    }
  ]
}

```



---

### `POST /api/execute`

Dispatches a reviewed task to the target provider.

* **Request:**
```json
{
  "task_id": "TSK-101",
  "tool": "JIRA",
  "payload": {
    "project": "PAYTM",
    "issue_type": "Bug Fix"
  }
}

```


* **Response:**
```json
{
  "status": "SUCCESS",
  "receipt_id": "PAYTM-3F1",
  "tool": "Jira Service Desk",
  "message": "Created Ticket PAYTM-3F1 for task TSK-101.",
  "state_change": "State updated: UNASSIGNED -> BACKLOG (BLOCKED BY DEPENDENCY)"
}

```



---

## Quick Start

### Prerequisites

* Python 3.10+
* Modern Chromium-based browser (Chrome, Edge, Brave)

### Installation

1. Clone the repository and enter the directory:
```bash
git clone <YOUR_REPOSITORY_URL>
cd opspilot

```


2. Install dependencies:
```bash
pip install fastapi uvicorn pydantic google-genai

```


3. Configure your API key (Optional—fallback mode activates if omitted):
* **Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
python backend.py

```


* **macOS / Linux:**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
python backend.py

```




4. Launch the dashboard:
* Open `index.html` directly in your browser.


---

## Project Structure

```text
opspilot/
├── backend.py        # FastAPI engine: /api/analyze, /api/execute, schemas & fallback
├── index.html        # Single-file dashboard (Tailwind CSS, state manager, HITL UI)
├── requirements.txt  # Python environment dependencies
└── README.md         # Project documentation & runbook

```

---

## Engineering Limitations & Roadmap

* **Mock Tool Execution:** Production deployments require OAuth token flows, rate limiting, and webhook validation for Jira, Google Workspace, and Slack.
* **Client-Enforced State:** Approval states currently manage in the client runtime; production setups should validate signatures on the server before dispatching.
* **Corpus Scale:** Designed for scoped messages. Long transcripts will use a retrieval-augmented chunking step before entity extraction.

---

## License

Distributed under the [MIT License](https://www.google.com/search?q=LICENSE&utm_source=gemini).

```

```
