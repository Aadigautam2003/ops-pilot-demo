# OpsPilot: Context-to-Action Executive Agent

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-8E75C2?style=flat&logo=googlegemini&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)
![Status](https://img.shields.io/badge/Status-Hackathon_Prototype-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> Turn messy workplace communication into approved, verifiable action.

OpsPilot reads an unstructured email, meeting note or chat thread and turns it into a dependency-ordered execution plan: who owns what, by when, what blocks what, and what is still unclear. Actions are dispatched to Jira, Calendar or Slack only after a human approves them.

It does not stop at a summary. Missing owners, vague times and conflicting dates are surfaced as explicit warnings instead of being guessed.

![OpsPilot dashboard](https://github.com/user-attachments/assets/7e39849d-a168-4e54-9513-ccd4fa7305ff)

> **Prototype scope:** task extraction is live (Gemini). Jira, Calendar and Slack dispatch are **simulated**. No external accounts are touched.

---

## How it works

```text
Unstructured text → Extraction → Uncertainty flags → Dependency graph → Human approval → Tool receipt
```

| Capability | What it does |
|---|---|
| **Structured extraction** | Gemini returns a JSON plan constrained to a fixed schema: tasks, owners, deadlines, priorities, tool targets. |
| **Uncertainty detection** | The prompt forbids inventing owners or dates. Gaps and conflicts come back as separate alerts with a recommended fix. |
| **Source grounding** | Each task carries a quoted snippet from the input. The backend checks that the snippet really appears in the text. If not, it lowers the task's confidence and adds a warning. |
| **Dependencies** | Tasks list prerequisite IDs. Invalid references are dropped, and the server refuses to dispatch a task until its prerequisites have been executed. |
| **Human approval** | The UI requires an explicit **Approve & Dispatch** click for every task. |
| **Receipts** | Each dispatch returns a receipt built from the task's own payload (ticket ID, event time, channel). |

Confidence values are the model's own estimate, not a calibrated probability.

## Architecture

```text
index.html  (Tailwind + vanilla JS)
     │  POST /api/analyze  { "text": "..." }
     ▼
backend.py  (FastAPI)
     ├─ Gemini call with JSON schema  ──►  verify snippets, clean dependencies  ──►  PlanResponse (source: "live")
     └─ Fallback demo plan (no key, or Gemini call fails)                       ──►  PlanResponse (source: "fallback")
     │
     ▼
Human review in the UI
     │  POST /api/execute  { task_id, tool, payload }
     ▼
Dependency check  ──►  simulated Jira / Calendar / Slack  ──►  receipt
```

### Fallback mode

If `GEMINI_API_KEY` is missing or the Gemini call raises an error, `/api/analyze` returns a fixed demo plan so the UI keeps working offline. That plan is the same for any input, so every response carries `"source": "live"` or `"source": "fallback"`, and the dashboard badge shows which one you got. If results look identical across different inputs, check the server log for the error.

## Quick start

Requires Python 3.10+ and a modern browser.

```bash
git clone <YOUR_REPOSITORY_URL>
cd opspilot
pip install -r requirements.txt    # fastapi, uvicorn, pydantic, google-genai
```

Set your Gemini API key as an environment variable. Never commit it.

```bash
# macOS / Linux
export GEMINI_API_KEY="your-key"

# Windows PowerShell
$env:GEMINI_API_KEY="your-key"
```

Optionally choose a model (default: `gemini-2.5-flash`):

```bash
export GEMINI_MODEL="gemini-2.5-flash"
```

Start the backend, then open `index.html` in your browser:

```bash
python backend.py     # http://127.0.0.1:8000  (interactive docs at /docs)
```

Without a key the app still runs, in fallback mode.

## API

### `POST /api/analyze`

```json
{ "text": "DevOps should fix the connection pool issue before Thursday..." }
```

Returns a `PlanResponse`:

```text
summary        string
source         "live" | "fallback"
uncertainties  [{ id, field, issue, recommended_action }]
tasks          [{
                 id, title,
                 assignee, assignee_status      CONFIRMED | UNCONFIRMED | MISSING
                 deadline, deadline_status      CONFIRMED | UNSPECIFIED
                 priority                       LOW | MEDIUM | HIGH | CRITICAL
                 grounded_snippet, confidence
                 dependencies                   IDs of prerequisite tasks
                 tool_target                    JIRA | CALENDAR | SLACK_ALERT
                 execution_payload, status
               }]
```

### `POST /api/execute`

```json
{ "task_id": "TSK-101", "tool": "JIRA", "payload": {} }
```

Success:

```json
{
  "status": "SUCCESS",
  "receipt_id": "PAYTM-3F1",
  "tool": "Jira (simulated)",
  "message": "Created ticket PAYTM-3F1: Patch DB Connection Pool.",
  "state_change": "Bug Fix created, priority High"
}
```

Errors: `404` if the task is not part of the current plan, `409` if it is blocked by tasks that have not been executed yet.

## Example

**Input**

```text
We should probably get the connection pool issue fixed before Thursday. DevOps
said they'll take a look, although I don't think we've confirmed who is actually
responsible for the DB failover. Sarah mentioned that we should have a final
checkpoint Friday morning before the production freeze. QA still needs to verify
the patch. Also, Mike can't attend Friday's meeting. We had some discussion about
moving the migration to Monday but I think we're still targeting Friday.
```

**Output (abridged)**

| Task | Owner | Due | Tool | Depends on |
|---|---|---|---|---|
| Patch DB connection pool | DevOps (unconfirmed) | Thursday EOD | Jira | none |
| QA verification on patch | missing | Before Friday morning | Jira | patch |
| Schedule production freeze review | Sarah | Friday morning | Calendar | QA |
| Execute production migration | Engineering leads | Friday night (tentative) | Slack | all above |

**Flagged as uncertain:** no named owner for the DB failover, no time for the Friday checkpoint, and Friday versus Monday for the migration.

## Demo flow (about 2.5 minutes)

1. **Analyze:** paste the sample and click *Analyze & Reason Over Plan*. Messy text becomes tasks with owners, deadlines and dependencies.
2. **Uncertainties:** show the warning panel. The agent flags the missing owner and the date conflict instead of guessing.
3. **Grounding:** click *Inspect Source* on a task to see the exact sentence it came from.
4. **Approve:** dispatch the unblocked task first. Blocked tasks stay locked until their prerequisites are done. Show the receipt.

## Project structure

```text
opspilot/
├── backend.py        FastAPI app: /api/analyze, /api/execute, schema, fallback plan
├── index.html        Single-file dashboard
├── requirements.txt  fastapi, uvicorn, pydantic, google-genai
└── README.md
```

## Limitations

- **Simulated tools.** Real Jira, Google Calendar and Slack integrations need OAuth, permissions, retries and audit logs.
- **Approval is a UI control.** The server enforces dependency order but does not verify that a human clicked Approve. A production version would require a signed approval.
- **Single-plan, in-memory state.** Analyzing new text replaces the previous plan, and state is lost on restart. There is no multi-user support.
- **Model-dependent quality.** Extraction accuracy depends on the LLM. Snippet verification catches fabricated quotes but not wrong interpretations.
- **Short inputs.** Built for single messages, not long transcripts.
- **Open CORS.** The backend allows all origins for local demo convenience.

## Roadmap

Real Jira/Calendar/Slack APIs, Gmail and Teams ingestion, signed approvals with audit logs, persistent task state, role-based permissions, and chunked processing for long transcripts.

## License

MIT
