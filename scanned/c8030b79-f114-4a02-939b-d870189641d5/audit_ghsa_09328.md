# [M] praisonai-platform: list_issue_activity returns activity log for any issue regardless of workspace ownership

## Summary
Severity: Medium
Advisory: GHSA-27p4-pjqv-whgj
CVE: CVE-2026-47408
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-27p4-pjqv-whgj
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Insecure Direct Object Reference. The `GET /workspaces/{workspace_id}/issues/{issue_id}/activity` endpoint is gated by `require_workspace_member(workspace_id)` and dispatches to `ActivityService.list_for_issue(issue_id)`, which executes `SELECT * FROM activity WHERE issue_id = :issue_id` with no workspace constraint. A user who is a member of any workspace can read the full activity log of any issue across the entire multi-tenant deployment.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/activity.py`, lines 32-43; `services/activity_service.py`'s `list_for_issue` method.

**Root cause:** the route extracts `workspace_id` from the URL path, uses it solely for the membership gate, then passes the URL-supplied `issue_id` directly to `ActivityService.list_for_issue(issue_id)` without verifying which workspace the issue belongs to. The companion `list_workspace_activity` endpoint at line 19-29 is implemented correctly (it passes `workspace_id` to `svc.list_for_workspace(workspace_id)`) — the asymmetry is the smoking gun.

## Affected Code

**File:** `src/praisonai-platform/praisonai_platform/api/routes/activity.py`, lines 19-43.

```python
@router.get("/activity", response_model=List[ActivityLogResponse])
async def list_workspace_activity(
    workspace_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = ActivityService(session)
    logs = await svc.list_for_workspace(workspace_id, limit=limit, offset=offset)  # correct: passes workspace_id
    return [ActivityLogResponse.model_validate(log) for log in logs]


@router.get("/issues/{issue_id}/activity", response_model=List[ActivityLogResponse])
async def list_issue_activity(
    workspace_id: str,
    issue_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = ActivityService(session)
    logs = await svc.list_for_issue(issue_id, limit=limit, offset=offset)  # <-- BUG: no workspace_id
    return [ActivityLogResponse.model_validate(log) for log in logs]
```

**Why it's wrong:** activity logs are typically the most sensitive operational record — they include actor identity, action type, entity references, and a free-form `details` JSON blob that may contain pre-/post-change values for any tracked field. Reading the foreign workspace's activity log gives the attacker a high-fidelity view into who did what when, which is gold for further reconnaissance (cross-workspace member enumeration, foreign issue title disclosure, knowing which projects exist). The same author got `list_workspace_activity` right by passing `workspace_id` — the issue-scoped variant is the gap.

## Exploit Chain

1. Attacker is a member of workspace `W_attacker` and harvests a target issue UUID `I_T` from any side channel. State: attacker holds `I_T`.
2. Attacker sends `GET /workspaces/W_attacker/issues/I_T/activity?limit=200` with `Authorization: Bearer <attacker_jwt>`. State: control flow enters `list_issue_activity`.
3. `require_workspace_member(W_attacker, attacker)` passes. `ActivityService.list_for_issue(I_T)` runs `SELECT * FROM activity WHERE issue_id = 'I_T' ORDER BY created_at DESC LIMIT 200`. State: response body is the full activity log for the foreign issue.
4. The activity entries reveal: every actor (member or agent) who touched the issue, every action (created, updated, commented, status_changed, assignee_changed, project_changed, label_added, dependency_added), and the `details` JSON blob containing the before/after values of every change. State: the attacker fingerprints the foreign workspace's triage workflow, identifies who works on what, and sees the issue's complete history including any embedded secrets that ever passed through the description or comments.
5. Final state: with one workspace-member token plus one GET, the attacker reads the full activity timeline of any issue in the multi-tenant deployment given the issue UUIDs.

## Security Impact

**Severity:** sec-moderate. CVSS 6.5: network attack, low complexity, low privileges, no user interaction, scope unchanged, high confidentiality (full activity log including before/after `details`), no integrity claim (read-only), no availability claim.

**Attacker capability:** read the activity log of any issue in the deployment given its UUID. Combined with the companion issue-IDOR (which already gives full issue content), this is recon for the foreign workspace's operational tempo, member identity, and triage workflow.

**Preconditions:** `praisonai-platform` is deployed multi-tenant; attacker has any workspace-membership token; foreign issue UUIDs are reachable.

**Differential:** source-inspection-verified. The asymmetry between `list_workspace_activity` (correctly workspace-scoped) and `list_issue_activity` (no workspace check) confirms the gap. With the suggested fix below, the route first resolves the issue via `IssueService.get(workspace_id, issue_id)`, returns 404 for foreign issues, and only then proceeds.

## Suggested Fix

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/activity.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/activity.py
@@ -32,9 +32,12 @@
 @router.get("/issues/{issue_id}/activity", response_model=List[ActivityLogResponse])
 async def list_issue_activity(
     workspace_id: str,
     issue_id: str,
     limit: int = Query(50, ge=1, le=200),
     offset: int = Query(0, ge=0),
     user: AuthIdentity = Depends(require_workspace_member),
     session: AsyncSession = Depends(get_db),
 ):
+    issue_svc = IssueService(session)
+    if await issue_svc.get(workspace_id, issue_id) is None:    # workspace-scoped get from issue-IDOR companion
+        raise HTTPException(status_code=404, detail="Issue not found")
     svc = ActivityService(session)
     logs = await svc.list_for_issue(issue_id, limit=limit, offset=offset)
     return [ActivityLogResponse.model_validate(log) for log in logs]
```

The same single-key issue lookup pattern is filed separately as the IssueService IDOR; once that is fixed, the helper used here is just `IssueService.get(workspace_id, issue_id)`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-27p4-pjqv-whgj
- https://github.com/MervinPraison/PraisonAI
