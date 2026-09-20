import os
import json
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from google import genai
from google.genai import types

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set. Set it via environment variable.")
    print("  Windows:  $env:GEMINI_API_KEY='your-key-here'; python backend.py")
    print("  Linux:    GEMINI_API_KEY='your-key-here' python backend.py")
client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="OpsPilot Agent Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class TaskItem(BaseModel):
    id: str
    title: str
    assignee: str
    assignee_status: str  # "CONFIRMED", "UNCONFIRMED", "MISSING"
    deadline: str
    deadline_status: str  # "CONFIRMED", "UNSPECIFIED"
    priority: str         # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    grounded_snippet: str
    confidence: float
    dependencies: List[str]
    tool_target: str       # "JIRA", "CALENDAR", "SLACK_ALERT"
    execution_payload: dict
    status: str = "PENDING_APPROVAL"

class UncertaintyAlert(BaseModel):
    id: str
    field: str
    issue: str
    recommended_action: str

class PlanResponse(BaseModel):
    summary: str
    uncertainties: List[UncertaintyAlert]
    tasks: List[TaskItem]

# --- Gemini Structured Output Schema ---
PLAN_SCHEMA = {
    "type": "OBJECT",
    "required": ["summary", "uncertainties", "tasks"],
    "properties": {
        "summary": {
            "type": "STRING",
            "description": "A one-line summary of the overall plan extracted from the input."
        },
        "uncertainties": {
            "type": "ARRAY",
            "description": "List of ambiguities, missing info, or conflicting details found in the input.",
            "items": {
                "type": "OBJECT",
                "required": ["id", "field", "issue", "recommended_action"],
                "properties": {
                    "id": {"type": "STRING", "description": "Unique ID like UNC-1, UNC-2, etc."},
                    "field": {"type": "STRING", "description": "The ambiguous field or topic."},
                    "issue": {"type": "STRING", "description": "What is unclear or missing."},
                    "recommended_action": {"type": "STRING", "description": "What the user should do to resolve this."}
                }
            }
        },
        "tasks": {
            "type": "ARRAY",
            "description": "List of actionable tasks extracted from the input, ordered by dependency.",
            "items": {
                "type": "OBJECT",
                "required": ["id", "title", "assignee", "assignee_status", "deadline", "deadline_status", "priority", "grounded_snippet", "confidence", "dependencies", "tool_target", "execution_payload"],
                "properties": {
                    "id": {"type": "STRING", "description": "Unique task ID like TSK-101, TSK-102, etc."},
                    "title": {"type": "STRING", "description": "Short descriptive title for the task."},
                    "assignee": {"type": "STRING", "description": "Person or team assigned. Use 'Unassigned' if unclear."},
                    "assignee_status": {"type": "STRING", "description": "One of: CONFIRMED, UNCONFIRMED, MISSING"},
                    "deadline": {"type": "STRING", "description": "Deadline mentioned or inferred. Use descriptive text."},
                    "deadline_status": {"type": "STRING", "description": "One of: CONFIRMED, UNSPECIFIED"},
                    "priority": {"type": "STRING", "description": "One of: LOW, MEDIUM, HIGH, CRITICAL"},
                    "grounded_snippet": {"type": "STRING", "description": "The EXACT verbatim quote from the input text that this task is based on. Must be a direct copy from the input."},
                    "confidence": {"type": "NUMBER", "description": "Confidence score between 0.0 and 1.0 for this extraction."},
                    "dependencies": {
                        "type": "ARRAY",
                        "description": "List of task IDs that must complete before this task.",
                        "items": {"type": "STRING"}
                    },
                    "tool_target": {"type": "STRING", "description": "One of: JIRA, CALENDAR, SLACK_ALERT. Choose the most appropriate tool for this task type."},
                    "execution_payload": {
                        "type": "OBJECT",
                        "description": "Key-value pairs relevant to the tool execution.",
                        "properties": {
                            "project": {"type": "STRING"},
                            "issue_type": {"type": "STRING"},
                            "priority": {"type": "STRING"},
                            "component": {"type": "STRING"},
                            "blocked_by": {"type": "STRING"},
                            "event_name": {"type": "STRING"},
                            "proposed_time": {"type": "STRING"},
                            "duration": {"type": "STRING"},
                            "channel": {"type": "STRING"},
                            "action": {"type": "STRING"}
                        }
                    }
                }
            }
        }
    }
}

SYSTEM_PROMPT = """You are OpsPilot, an autonomous workflow extraction agent. Your job is to analyze unstructured communications (emails, meeting notes, Slack messages) and extract:

1. **Tasks**: Concrete actionable items with owners, deadlines, priorities, and dependencies.
2. **Uncertainties**: Anything ambiguous, missing, or conflicting — do NOT hallucinate or guess.
3. **Source Grounding**: Every task MUST include the exact verbatim snippet from the input it was derived from.

Rules:
- Task IDs must be sequential: TSK-101, TSK-102, TSK-103, etc.
- Uncertainty IDs must be sequential: UNC-1, UNC-2, UNC-3, etc.
- If an owner is not explicitly named, set assignee_status to "MISSING" or "UNCONFIRMED".
- If a deadline is vague (e.g., "soon", "next week"), set deadline_status to "UNSPECIFIED".
- Build a dependency graph: if Task B can only start after Task A, add Task A's ID to Task B's dependencies.
- Choose tool_target based on task type:
  - JIRA: for bug fixes, development tasks, QA tasks, tickets
  - CALENDAR: for meetings, reviews, checkpoints, syncs
  - SLACK_ALERT: for notifications, broadcasts, alerts, announcements
- Confidence score: 0.9+ for explicit clear tasks, 0.7-0.9 for inferred tasks, below 0.7 for speculative tasks.
- grounded_snippet MUST be a direct verbatim quote from the input text, not a paraphrase.
- Extract ALL actionable items, even implicit ones.
- If the input has no actionable items, return empty tasks and uncertainties lists with an appropriate summary."""

@app.post("/api/analyze", response_model=PlanResponse)
async def analyze_document(payload: dict):
    input_text = payload.get("text", "")

    if not input_text.strip():
        return PlanResponse(summary="No input provided.", uncertainties=[], tasks=[])

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Analyze the following communication and extract the execution plan:\n\n---\n{input_text}\n---",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=PLAN_SCHEMA,
                temperature=0.2,
            ),
        )

        result = json.loads(response.text)

        # Ensure all tasks have a default status
        for task in result.get("tasks", []):
            if "status" not in task:
                task["status"] = "PENDING_APPROVAL"

        return PlanResponse(**result)

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return PlanResponse(
            summary=f"Error analyzing input: {str(e)}",
            uncertainties=[],
            tasks=[]
        )

# --- Execution Simulation ---
class ActionRequest(BaseModel):
    task_id: str
    tool: str
    payload: dict

@app.post("/api/execute")
async def execute_tool(req: ActionRequest):
    receipt_id = f"RCP-{uuid.uuid4().hex[:6].upper()}"

    if req.tool == "JIRA":
        ticket_id = f"PROJ-{uuid.uuid4().hex[:3].upper()}"
        return {
            "status": "SUCCESS",
            "receipt_id": ticket_id,
            "tool": "Jira Service Desk",
            "message": f"Created Ticket {ticket_id} for task {req.task_id}.",
            "state_change": f"State changed: UNASSIGNED -> BACKLOG"
        }
    elif req.tool == "CALENDAR":
        return {
            "status": "SUCCESS",
            "receipt_id": receipt_id,
            "tool": "Google Calendar API",
            "message": f"Calendar event created for task {req.task_id}.",
            "state_change": "Invites dispatched to all mentioned participants."
        }
    else:
        return {
            "status": "SUCCESS",
            "receipt_id": receipt_id,
            "tool": "Slack Bot Dispatcher",
            "message": f"Broadcast sent for task {req.task_id}.",
            "state_change": "Notification dispatched to relevant channels."
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
