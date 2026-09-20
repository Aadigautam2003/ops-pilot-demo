# OpsPilot — Context-to-Action Executive Agent

![Status](https://img.shields.io/badge/Status-Demo-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Turn messy communication into approved action.**

OpsPilot is an AI-powered workflow agent that transforms chaotic workplace communication such as emails, meeting notes, project updates, and Slack-style conversations into **structured, dependency-aware execution plans**.

Instead of simply summarizing information, OpsPilot identifies **what needs to happen, who is responsible, when it needs to happen, what is uncertain, and what actions should be taken next**.

Before any external action is dispatched, a human reviews and approves the proposed action.

---

## 🎯 Problem

Modern teams receive important information through unstructured communication:

* Emails
* Meeting notes
* Project updates
* Chat messages
* Status reports
* Requirements documents

These messages often contain a mixture of:

* Tasks
* Deadlines
* People and teams
* Priorities
* Dependencies
* Decisions
* Missing information
* Conflicting requirements

Turning this information into actual work usually requires manual effort.

For example:

> "DevOps should probably get the connection pool issue fixed before Thursday. We still haven't confirmed who's handling the DB failover. Sarah wants a final checkpoint Friday morning before the production freeze. QA also needs to verify the patch."

A human has to determine:

```text
What are the tasks?
Who owns them?
When are they due?
What depends on what?
What information is missing?
What should happen next?
```

**OpsPilot automates this process while keeping the human in control of execution.**

---

# 💡 Solution

OpsPilot creates an end-to-end workflow:

```text
Unstructured Communication
          │
          ▼
   AI Understanding
          │
          ▼
Structured Task Extraction
          │
          ├── Tasks
          ├── Owners
          ├── Deadlines
          ├── Priorities
          └── Decisions
          │
          ▼
 Uncertainty Detection
          │
          ▼
 Dependency Analysis
          │
          ▼
   Execution Plan
          │
          ▼
 Human Review & Approval
          │
          ▼
     Tool Dispatch
          │
      ┌───┼────┐
      ▼   ▼    ▼
    Jira Calendar Slack
      │   │    │
      └───┼────┘
          ▼
   Execution Receipt
```

The core principle is:

> **Understand → Plan → Verify → Approve → Execute**

---

# ✨ Key Features

## 1. Unstructured Input Parsing

Users can provide chaotic workplace communication directly to OpsPilot.

Supported demo input includes:

* Project updates
* Meeting notes
* Emails
* Slack-style conversations

The system converts natural language into structured information.

---

## 2. Structured Task Extraction

OpsPilot identifies actionable tasks and extracts relevant attributes.

Example:

```text
Task:
Fix database connection pool

Owner:
DevOps Team

Deadline:
Thursday

Priority:
High

Action:
Create Jira ticket
```

---

## 3. Dependency-Aware Planning

OpsPilot identifies relationships between tasks.

For example:

```text
Fix Database Patch
        │
        ▼
   QA Verification
        │
        ▼
Production Checkpoint
        │
        ▼
 Production Migration
```

This allows the agent to understand that some actions should happen before others.

---

## 4. Uncertainty Detection

OpsPilot does not automatically invent missing information.

For example, if the source says:

> "Someone from DevOps should handle the DB failover."

OpsPilot can flag:

```text
⚠ Uncertainty Detected

DB failover owner is not explicitly specified.

Action requires confirmation.
```

Other examples include:

* Missing task owner
* Ambiguous deadline
* Missing meeting time
* Conflicting dates
* Unclear responsibility

---

## 5. Source Grounding

Every extracted task can be traced back to the original source.

Example:

```text
Task
Fix database connection pool

Confidence
96%

Source
"DevOps should get the connection pool issue
fixed before Thursday."
```

This allows users to verify why the agent created a particular task.

---

## 6. Confidence Scoring

Each extracted task includes a confidence score representing how clearly the task was identified from the source.

Example:

```text
Fix database connection pool
Confidence: 0.96
```

While ambiguous information can receive a lower confidence score and be accompanied by an uncertainty warning.

---

## 7. Human-in-the-Loop Approval

OpsPilot does not blindly execute every action.

Instead:

```text
AI proposes action
       │
       ▼
Human reviews
       │
   ┌───┴────┐
   ▼        ▼
Approve   Reject
   │
   ▼
Execute
```

This creates a controlled workflow for actions that may affect external systems.

---

## 8. Tool Dispatch

The prototype supports simulated tool dispatch for actions such as:

* Jira ticket creation
* Calendar event creation
* Slack notifications

The current hackathon implementation uses simulated execution so that the complete workflow can be demonstrated without requiring external account credentials.

---

## 9. Visual Execution Receipts

After an approved action is dispatched, OpsPilot displays an execution receipt.

Example:

```text
✓ ACTION EXECUTED

Jira Ticket Created

PAYTM-402

Task:
Database connection pool patch

Priority:
HIGH

Status:
OPEN
```

This provides visible confirmation that the workflow progressed from planning to execution.

---

# 🏗️ System Architecture

```text
┌───────────────────────────────────────────────────────┐
│                    OPSPILOT                           │
└───────────────────────────────────────────────────────┘

             UNSTRUCTURED INPUT
        ┌─────────────────────────┐
        │ Email / Notes / Message │
        └────────────┬────────────┘
                     │
                     │ HTTP
                     ▼
        ┌─────────────────────────┐
        │       FRONTEND          │
        │       index.html        │
        │                         │
        │ • Input interface       │
        │ • Task cards            │
        │ • Uncertainty panel     │
        │ • Source inspection     │
        │ • Approval controls     │
        │ • Execution receipts    │
        └────────────┬────────────┘
                     │
             POST /api/analyze
                     │
                     ▼
        ┌─────────────────────────┐
        │       FASTAPI           │
        │       backend.py        │
        │                         │
        │  Analysis Engine        │
        │  ├─ Task Extraction     │
        │  ├─ Entity Extraction   │
        │  ├─ Deadline Detection  │
        │  ├─ Priority Detection  │
        │  ├─ Uncertainty Flags   │
        │  └─ Dependency Analysis │
        └────────────┬────────────┘
                     │
                     ▼
              STRUCTURED PLAN
                     │
                     ▼
        ┌─────────────────────────┐
        │    HUMAN APPROVAL       │
        │                         │
        │ Review → Approve/Reject │
        └────────────┬────────────┘
                     │
             POST /api/execute
                     │
                     ▼
        ┌─────────────────────────┐
        │     TOOL DISPATCHER     │
        │                         │
        │   ┌─────┐ ┌────────┐    │
        │   │Jira │ │Calendar│    │
        │   └─────┘ └────────┘    │
        │                         │
        │       ┌───────┐         │
        │       │ Slack │         │
        │       └───────┘         │
        │                         │
        │    Simulated Tools      │
        └────────────┬────────────┘
                     │
                     ▼
             EXECUTION RECEIPT
```

---

# 🔄 End-to-End Workflow

### Step 1 — Input

The user provides an unstructured communication.

```text
"DevOps should fix the connection pool
before Thursday. QA needs to verify it..."
```

### Step 2 — Analysis

OpsPilot processes the text and identifies:

```text
Tasks
People
Deadlines
Priorities
Dependencies
Uncertainties
```

### Step 3 — Planning

The extracted information is converted into an execution plan.

```text
Task 1 → Fix connection pool
Task 2 → QA verification
Task 3 → Schedule checkpoint
Task 4 → Production migration
```

### Step 4 — Grounding

Each task can be traced back to the original text.

### Step 5 — Uncertainty Detection

The system identifies information that is missing or ambiguous.

```text
⚠ Owner not specified
⚠ Exact time not specified
⚠ Conflicting migration date
```

### Step 6 — Human Approval

The user reviews the proposed action.

```text
[ Approve & Dispatch ]
```

### Step 7 — Tool Execution

The approved task is sent to the corresponding tool.

```text
Task → Jira
```

### Step 8 — Execution Receipt

The interface displays the result.

```text
✓ Jira Ticket PAYTM-402 Created
```

---

# 🧠 Core Components

## Frontend

**Technology:** HTML, CSS, JavaScript, Tailwind CSS

Responsibilities:

* Accept user input
* Display analysis results
* Display uncertainties
* Display extracted tasks
* Show source grounding
* Request human approval
* Display execution results

---

## Backend

**Technology:** Python + FastAPI + Pydantic

Responsibilities:

* Receive user input
* Analyze and structure information
* Generate the execution plan
* Track uncertainty
* Process execution requests
* Return execution receipts

---

## Analysis Engine

The analysis engine converts unstructured communication into structured objects.

Conceptually:

```text
Raw Text
   ↓
Task Extraction
   ↓
Entity Extraction
   ↓
Deadline Detection
   ↓
Priority Detection
   ↓
Uncertainty Detection
   ↓
Dependency Analysis
   ↓
PlanResponse
```

---

## Tool Dispatcher

The tool dispatcher determines which action should be performed.

Example:

```text
Action Type: JIRA_TICKET
        ↓
Jira Tool
        ↓
Execution Receipt
```

Future integrations could connect the same interface to real external APIs.

---

# 📡 API Architecture

## `POST /api/analyze`

Analyzes unstructured text and produces a structured execution plan.

### Request

```json
{
  "text": "Hey everyone, quick update from today's call..."
}
```

### Response

The response contains:

```text
PlanResponse
├── summary
├── uncertainties[]
└── tasks[]
      ├── id
      ├── task
      ├── assignee
      ├── deadline
      ├── priority
      ├── confidence
      ├── source_snippet
      ├── dependencies[]
      └── tool
```

---

## `POST /api/execute`

Dispatches an approved task.

### Request

```json
{
  "task_id": "TSK-101",
  "tool": "JIRA",
  "payload": {}
}
```

### Response

```json
{
  "status": "SUCCESS",
  "receipt_id": "PAYTM-402",
  "state_change": "Jira ticket created"
}
```

---

# 🚀 Quick Start

## Prerequisites

* Python 3.10+
* Modern web browser

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ops-pilot-demo
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or:

```bash
pip install fastapi uvicorn pydantic
```

## 3. Start the backend

```bash
python backend.py
```

The FastAPI server will start at:

```text
http://127.0.0.1:8000
```

## 4. Open the frontend

Open:

```text
index.html
```

in a modern browser.

---

# 📁 Project Structure

```text
ops-pilot-demo/
│
├── backend.py
│   └── FastAPI backend
│       ├── /api/analyze
│       ├── /api/execute
│       ├── task extraction
│       ├── uncertainty detection
│       └── tool dispatch simulation
│
├── index.html
│   └── Frontend dashboard
│       ├── Input interface
│       ├── Analysis results
│       ├── Uncertainty panel
│       ├── Task cards
│       ├── Source grounding
│       └── Execution receipts
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│
└── README.md
```

---

# 🎬 Hackathon Demo

The recommended demo takes approximately 2.5 minutes.

| Time      | Action                        | What to demonstrate                                             |
| --------- | ----------------------------- | --------------------------------------------------------------- |
| 0:00–0:30 | Analyze chaotic communication | Unstructured text becomes structured tasks                      |
| 0:30–1:15 | Show uncertainty panel        | Missing owner, ambiguous time and conflicting information       |
| 1:15–1:45 | Inspect task source           | Task is grounded in the original text                           |
| 1:45–2:30 | Approve & Dispatch            | Human approval triggers tool execution and an execution receipt |

### Demo narrative

Start with:

> "This is a typical project update. It contains useful information, but it's mixed with ambiguity, deadlines and dependencies."

Click **Analyze & Reason Over Plan**.

Then show:

```text
4 Tasks
3 High Priority
3 Uncertainties
```

Highlight the uncertainty:

> "Instead of inventing an owner, OpsPilot tells us that the owner is missing."

Open **Inspect Source**:

> "Every extracted task can be traced back to the original communication."

Finally:

> "Now I'll approve the action."

Click **Approve & Dispatch**.

Show:

```text
✓ PAYTM-402
Jira Ticket Created
```

The key message:

> **OpsPilot doesn't just summarize the communication. It turns the communication into an approved execution workflow.**

---

# 🔐 Human-in-the-Loop Safety

OpsPilot separates **planning** from **execution**.

The AI can propose:

```text
Create Jira ticket
Schedule meeting
Send notification
```

But the action is not dispatched until the user approves it.

```text
AI PLAN
   │
   ▼
Human Review
   │
   ├── Reject → Stop
   │
   └── Approve
          │
          ▼
      Tool Call
```

This provides a control point before actions that could affect external systems.

---

# 🧪 Current Demo vs. Production Version

The current hackathon version focuses on demonstrating the complete workflow.

### Current Demo

```text
✓ Unstructured input
✓ Structured task extraction
✓ Dependency representation
✓ Uncertainty detection
✓ Source grounding
✓ Confidence scores
✓ Human approval
✓ Simulated tool execution
✓ Execution receipts
```

### Production Extension

A production implementation could replace the deterministic analysis and simulated tools with:

```text
                Production OpsPilot

Input Sources
   │
   ├── Gmail
   ├── Slack
   ├── Microsoft Teams
   └── Documents
          │
          ▼
      LLM / Agent
          │
          ▼
    Structured Output
          │
          ▼
      RAG / Vector DB
          │
          ▼
     Task Planner
          │
          ▼
    Approval Layer
          │
          ▼
      Tool APIs
          │
     ┌────┼────┐
     ▼    ▼    ▼
   Jira Calendar Slack
```

Real integrations would require authentication, permissions, API error handling, retries, audit logs and appropriate access controls.

---

# 🔮 Future Improvements

Potential extensions include:

* Real Jira API integration
* Google Calendar integration
* Slack integration
* Gmail ingestion
* Microsoft Teams integration
* RAG over historical project documentation
* Persistent task state
* Advanced dependency graphs
* Automatic conflict resolution suggestions
* Role-based permissions
* Audit logs
* Action rollback
* Multi-agent planning
* Evaluation using task completion and grounding metrics

---

# 📊 Example

### Input

```text
"DevOps should get the connection pool fix
done before Thursday. QA needs to verify the
patch. We still haven't decided who owns the
DB failover. Sarah wants a checkpoint Friday
morning before the production freeze."
```

### OpsPilot Output

```text
SUMMARY
Prepare the database patch and production
readiness workflow.

TASK 1
Fix connection pool
Owner: DevOps
Deadline: Thursday
Priority: High
Confidence: 0.96
Action: Jira

TASK 2
Verify database patch
Owner: Unassigned
Deadline: Before production freeze
Priority: High
Confidence: 0.84
Action: Jira

TASK 3
Schedule production checkpoint
Owner: Sarah
Deadline: Friday morning
Priority: High
Confidence: 0.91
Action: Calendar
```

### Uncertainty

```text
⚠ DB failover owner is not specified.
⚠ Exact checkpoint time is not specified.
```

### Approved execution

```text
Human:
Approve Task 1

        ↓

Tool:
Jira

        ↓

Result:
✓ PAYTM-402 created
```

---

# 🏆 Why OpsPilot?

Most productivity assistants stop at:

```text
Understand → Summarize
```

OpsPilot is designed around:

```text
Understand
     ↓
Extract
     ↓
Detect uncertainty
     ↓
Plan
     ↓
Ground
     ↓
Human approval
     ↓
Execute
     ↓
Report result
```

The goal is not to replace the human decision-maker.

The goal is to remove the repetitive work between **receiving information and taking action**.

---

# 📜 License

MIT License
