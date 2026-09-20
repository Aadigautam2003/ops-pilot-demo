# OpsPilot: Context-to-Action Executive Agent

OpsPilot turns messy workplace communication (emails, meeting notes, Slack-style updates) into a dependency-aware execution plan, then dispatches actions only after a human approves them.

It does more than summarize. For each message it works out what needs to happen, who owns it, when it is due, what depends on what, and what is still unclear. Missing or conflicting information is flagged instead of guessed.

> Understand → Extract → Flag uncertainty → Plan → Approve → Execute

**Status:** hackathon prototype. Extraction uses the Gemini API. Tool dispatch (Jira, Calendar, Slack) is **simulated**; no external accounts are called.

---
![Uploading image.png…]()


## What it does

1. **Structured extraction.** Gemini returns a JSON plan constrained to a fixed schema: a summary, a list of uncertainties, and a list of tasks.
2. **Uncertainty detection.** The prompt tells the model not to invent owners or dates. Ambiguities come back as separate alerts, each with a recommended action.
3. **Source grounding.** Each task carries a `grounded_snippet`, a quote from the input the model says the task came from.
4. **Confidence scores.** Each task has a model-reported confidence between 0 and 1. It is a self-assessment, not a calibrated probability.
5. **Dependencies.** Tasks list prerequisite task IDs, so ordering constraints (patch → QA → checkpoint → migration) are explicit.
6. **Human approval.** Nothing is dispatched until the user clicks Approve in the UI.
7. **Simulated dispatch and receipts.** Approved tasks go to a mock Jira, Calendar or Slack handler, which returns a receipt.

## Architecture

```text
index.html (frontend)
   │  POST /api/analyze   { "text": "..." }
   ▼
backend.py (FastAPI)
   ├─ Gemini structured-output call  ──►  PlanResponse
   └─ Deterministic fallback plan (if no API key or the call fails)
   │
   ▼
Human review in the UI
   │  POST /api/execute   { task_id, tool, payload }
   ▼
Simulated tool handlers (JIRA / CALENDAR / SLACK_ALERT)  ──►  receipt
```

**Frontend:** HTML, CSS, JavaScript, Tailwind. Shows the plan, uncertainties, source snippets and approval controls.
**Backend:** Python, FastAPI, Pydantic, `google-genai`.

### Fallback mode

If `GEMINI_API_KEY` is unset, or the Gemini call raises an error, `/api/analyze` returns a fixed demo plan (a database patch / production freeze scenario) regardless of the input. This keeps the demo running offline. The server log prints which path was taken. Check it if the output looks identical across different inputs.

## API

### `POST /api/analyze`

Request:

```json
{ "text": "Hey everyone, quick update from today's call..." }
```

Response (`PlanResponse`):

```text
summary: string
uncertainties[]: { id, field, issue, recommended_action }
tasks[]:
  id, title
  assignee, assignee_status        CONFIRMED | UNCONFIRMED | MISSING
  deadline, deadline_status        CONFIRMED | UNSPECIFIED
  priority                         LOW | MEDIUM | HIGH | CRITICAL
  grounded_snippet, confidence
  dependencies[]                   IDs of prerequisite tasks
  tool_target                      JIRA | CALENDAR | SLACK_ALERT
  execution_payload                tool-specific parameters
  status                           PENDING_APPROVAL
```

### `POST /api/execute`

Request:

```json
{ "task_id": "TSK-101", "tool": "JIRA", "payload": {} }
```

Response (simulated):

```json
{
  "status": "SUCCESS",
  "receipt_id": "PAYTM-3F1",
  "tool": "Jira Service Desk",
  "message": "Created Ticket PAYTM-3F1 for task TSK-101.",
  "state_change": "State updated: UNASSIGNED -> BACKLOG (BLOCKED BY DEPENDENCY)"
}
```

Receipt IDs are randomly generated. Any `tool` value other than `JIRA` or `CALENDAR` is handled as a Slack alert.

## Quick start

Requires Python 3.10+ and a modern browser.

```bash
git clone <YOUR_REPOSITORY_URL>
cd <repo-directory>
pip install -r requirements.txt   # fastapi, uvicorn, pydantic, google-genai

export GEMINI_API_KEY=your_key    # optional; omit to run in fallback mode
python backend.py                 # serves on http://127.0.0.1:8000
```

Then open `index.html` in a browser.

## Project structure

```text
backend.py        FastAPI app: /api/analyze, /api/execute, schema, fallback plan
index.html        Frontend dashboard
requirements.txt  Python dependencies
README.md
```

## Example

**Input**

```text
DevOps should get the connection pool fix done before Thursday. QA still
needs to verify the patch. We haven't decided who owns the DB failover.
Sarah wants a checkpoint Friday morning before the production freeze. We
talked about moving the migration to Monday but I think we're still
targeting Friday.
```

**Output (abridged)**

| Task | Owner | Deadline | Tool | Depends on |
|---|---|---|---|---|
| Patch DB connection pool | DevOps Team (unconfirmed) | Thursday EOD | Jira | none |
| QA verification on patch | missing | Before Friday morning | Jira | patch |
| Schedule production freeze review | Sarah | Friday morning (no time given) | Calendar | QA |
| Execute production migration | Engineering leads | Friday night (tentative) | Slack | all above |

**Uncertainties flagged:** no named owner for the DB failover; the Friday checkpoint has no time slot; Friday and Monday are both mentioned for the migration.

## Demo flow (about 2.5 minutes)

| Time | Step | Point to make |
|---|---|---|
| 0:00–0:30 | Paste the sample update and click Analyze | Unstructured text becomes tasks with owners, deadlines and dependencies |
| 0:30–1:15 | Open the uncertainty panel | The agent flags the missing owner and conflicting dates instead of guessing |
| 1:15–1:45 | Inspect a task's source snippet | Each task points back to the original text |
| 1:45–2:30 | Approve & Dispatch | Execution only happens after human approval, and a receipt confirms it |

## Limitations

- **Tools are simulated.** Real Jira, Google Calendar and Slack integrations would need OAuth, permissions, retries, error handling and audit logging.
- **Approval is enforced in the UI only.** `/api/execute` does not check that a task was approved or that its dependencies have run.
- **Grounding is not verified server-side.** Snippets are requested verbatim from the model but not checked against the input.
- **Confidence is self-reported by the model.**
- **No persistence.** Plans and execution state are not stored.
- **Fallback plan is fixed.** It only matches the built-in demo scenario.
- **Execution ignores most of the payload.** The Calendar and Slack receipts use fixed text.

## Future work

Real Jira, Calendar and Slack APIs; Gmail and Teams ingestion; server-side approval and dependency checks; verbatim-snippet validation; persistent task state; audit logs and role-based permissions; retrieval over past project documentation.

## License

MIT
