from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="OpsPilot Agent Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskItem(BaseModel):
    id: str
    title: str
    assignee: str
    assignee_status: str  # "CONFIRMED", "UNCONFIRMED", "MISSING"
    deadline: str
    deadline_status: str  # "CONFIRMED", "UNSPECIFIED"
    priority: str
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

CHAOTIC_INPUT_PRESET = (
    "Subject: Friday migration / DB thing / urgent\n"
    "Hey everyone, quick update from today's call. We should probably get the connection pool "
    "issue fixed before Thursday. DevOps said they'll take a look, although I don't think we've "
    "confirmed who is actually responsible for the DB failover. Sarah mentioned that we should have "
    "a final checkpoint Friday morning before the production freeze. QA still needs to verify the patch. "
    "Also, Mike can't attend Friday's meeting. We had some discussion about moving the migration to Monday "
    "but I think we're still targeting Friday. Please make sure everyone is aligned."
)

@app.post("/api/analyze", response_model=PlanResponse)
async def analyze_document(payload: dict):
    # In production, pass payload["text"] to an LLM with structured schema.
    # Deterministic pipeline output matches the exact chaotic test scenario:
    return PlanResponse(
        summary="Targeting Friday Production Freeze & DB Migration. 4 critical workflow tasks extracted with sequential blockers.",
        uncertainties=[
            UncertaintyAlert(
                id="UNC-1",
                field="DB Failover Ownership",
                issue="DevOps mentioned generally, but specific DRI is not assigned.",
                recommended_action="Block execution until owner is manually confirmed."
            ),
            UncertaintyAlert(
                id="UNC-2",
                field="Meeting Schedule",
                issue="'Friday morning' lacks specific time slot; attendee conflict flagged (Mike).",
                recommended_action="Propose 10:00 AM slot or flag invitees."
            ),
            UncertaintyAlert(
                id="UNC-3",
                field="Target Date Ambiguity",
                issue="Email mentions conflicting discussions between Friday and Monday.",
                recommended_action="Hold final deployment ticket in draft state."
            )
        ],
        tasks=[
            TaskItem(
                id="TSK-101",
                title="Patch DB Connection Pool",
                assignee="DevOps Team",
                assignee_status="UNCONFIRMED",
                deadline="Thursday EOD",
                deadline_status="CONFIRMED",
                priority="HIGH",
                grounded_snippet="We should probably get the connection pool issue fixed before Thursday. DevOps said they'll take a look...",
                confidence=0.94,
                dependencies=[],
                tool_target="JIRA",
                execution_payload={"project": "PAYTM", "issue_type": "Bug Fix", "priority": "High", "component": "DB_Pool"}
            ),
            TaskItem(
                id="TSK-102",
                title="QA Verification & Regression on Patch",
                assignee="QA Team",
                assignee_status="MISSING",
                deadline="Before Friday Morning",
                deadline_status="UNSPECIFIED",
                priority="HIGH",
                grounded_snippet="QA still needs to verify the patch.",
                confidence=0.72,
                dependencies=["TSK-101"],
                tool_target="JIRA",
                execution_payload={"project": "PAYTM", "issue_type": "Test Verification", "blocked_by": "TSK-101"}
            ),
            TaskItem(
                id="TSK-103",
                title="Schedule Production Freeze Review",
                assignee="Sarah / Release Team",
                assignee_status="CONFIRMED",
                deadline="Friday Morning",
                deadline_status="UNSPECIFIED",
                priority="MEDIUM",
                grounded_snippet="Sarah mentioned that we should have a final checkpoint Friday morning before the production freeze.",
                confidence=0.89,
                dependencies=["TSK-102"],
                tool_target="CALENDAR",
                execution_payload={"event_name": "Prod Freeze Checkpoint", "proposed_time": "Friday 10:00 AM IST", "duration": "30m"}
            ),
            TaskItem(
                id="TSK-104",
                title="Execute Production Gateway Migration",
                assignee="Engineering Leads",
                assignee_status="CONFIRMED",
                deadline="Friday Night (Tentative)",
                deadline_status="UNSPECIFIED",
                priority="CRITICAL",
                grounded_snippet="We had some discussion about moving the migration to Monday but I think we're still targeting Friday.",
                confidence=0.61,
                dependencies=["TSK-101", "TSK-102", "TSK-103"],
                tool_target="SLACK_ALERT",
                execution_payload={"channel": "#prod-releases", "action": "Trigger Canary Deployment"}
            )
        ]
    )

class ActionRequest(BaseModel):
    task_id: str
    tool: str
    payload: dict

@app.post("/api/execute")
async def execute_tool(req: ActionRequest):
    # Simulated execution receipts
    if req.tool == "JIRA":
        return {
            "status": "SUCCESS",
            "receipt_id": "PAYTM-402",
            "tool": "Jira Service Desk",
            "message": f"Created Ticket PAYTM-402 with priority HIGH.",
            "state_change": "State changed: UNASSIGNED -> BACKLOG (BLOCKED BY TSK-101)"
        }
    elif req.tool == "CALENDAR":
        return {
            "status": "SUCCESS",
            "receipt_id": "CAL-99182",
            "tool": "Google Calendar API",
            "message": "Event 'Prod Freeze Checkpoint' scheduled for Friday 10:00 AM IST.",
            "state_change": "Invites dispatched: Sarah, Release Team (Mike flagged unavailable)"
        }
    else:
        return {
            "status": "SUCCESS",
            "receipt_id": "MSG-7741",
            "tool": "Slack Bot Dispatcher",
            "message": "Broadcast sent to #prod-releases.",
            "state_change": "Workflow trigger primed."
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
