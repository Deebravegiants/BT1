# [H] praisonai-platform: Any workspace member can delete the entire workspace via DELETE /workspaces/{id}

## Summary
Severity: High
Advisory: GHSA-g8rr-7rj2-f627
CVE: CVE-2026-47412
CWE: CWE-269, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-g8rr-7rj2-f627
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Authorization bypass enabling destructive action. The `DELETE /workspaces/{workspace_id}` endpoint is gated only by `require_workspace_member(workspace_id)` (default `min_role="member"`). Any member of the workspace can issue a single DELETE to wipe the entire workspace, including every project, issue, comment, agent, label, and member record (cascading via the foreign-key relationships). There is no owner-role gate, no confirmation token, no soft-delete window, no recovery path.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 77-86; `services/workspace_service.py`'s `delete()` method.
**Root cause:** the route uses `Depends(require_workspace_member)` which defaults to `min_role="member"` and is never overridden. The service method `WorkspaceService.delete(workspace_id)` performs the destructive operation without any caller-permission verification. The role hierarchy (`MemberService.has_role`, member_service.py:80-96) is implemented but unused for this endpoint.

## Affected Code

**File:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 77-86.

```python
@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    user: AuthIdentity = Depends(require_workspace_member),         # <-- BUG: defaults to min_role="member"
    session: AsyncSession = Depends(get_db),
):
    ws_svc = WorkspaceService(session)
    deleted = await ws_svc.delete(workspace_id)                     # <-- destructive, no role check
    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")
```

**Why it's wrong:** workspace deletion is the most destructive single action in this product — it wipes every member, project, issue, comment, agent, and label belonging to the tenant. The standard convention is to gate this on owner role, ideally with a confirmation parameter (typed workspace name) and a recovery window. This endpoint does none of that. The `require_workspace_member(min_role)` parameter exists precisely for this kind of tightening but is never invoked with anything other than the default.

## Exploit Chain

1. Attacker is a member of workspace `W` (joined via invite, signup default, or any other route into membership). State: attacker holds JWT with `Member(workspace_id=W, user_id=attacker, role="member")`.
2. Attacker sends `DELETE /workspaces/W` with `Authorization: Bearer <attacker_jwt>`. State: control flow enters `delete_workspace`.
3. `require_workspace_member(W, attacker)` passes (attacker is a member, default min_role="member" satisfied). `WorkspaceService.delete(W)` removes the workspace row; SQLAlchemy cascade rules drop every related row (members, projects, issues, comments, agents, labels). State: workspace `W` no longer exists.
4. Final state: a low-privilege member has wiped the workspace. The legitimate owner has no recovery: no soft-delete, no audit-trail event for the deletion (the `Activity` log row would have been deleted too as part of the cascade). The same primitive at scale (script that DELETEs every workspace_id the attacker can enumerate) becomes a multi-tenant griefing tool.

## Security Impact

**Severity:** sec-high. CVSS 8.1: network attack, low complexity, low privileges, no user interaction, scope unchanged, no confidentiality (just destruction), high integrity (every workspace child row wiped), high availability (workspace gone for legitimate owner).
**Attacker capability:** with one workspace-member token plus one DELETE request, the attacker irreversibly deletes the workspace and every child resource. The deletion is silent and immediate.
**Preconditions:** `praisonai-platform` is deployed multi-tenant; the attacker has any membership token in the target workspace.
**Differential:** source-inspection-verified. The asymmetry between `require_workspace_member`'s clearly-tunable `min_role` parameter and this endpoint's use of the default value confirms the gap. With the suggested fix below, member-tier tokens fail the gate at the dependency, the destructive action never reaches the service layer, and the endpoint returns 403 instead of 204.

## Suggested Fix

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
@@ -75,11 +75,15 @@
+def _require_workspace_owner(workspace_id: str, user, session):
+    return require_workspace_member(workspace_id, user, session, min_role="owner")
+
 @router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
 async def delete_workspace(
     workspace_id: str,
-    user: AuthIdentity = Depends(require_workspace_member),
+    user: AuthIdentity = Depends(_require_workspace_owner),
     session: AsyncSession = Depends(get_db),
 ):
     ws_svc = WorkspaceService(session)
     deleted = await ws_svc.delete(workspace_id)
     if not deleted:
         raise HTTPException(status_code=404, detail="Workspace not found")
```

Defence-in-depth: require a typed-confirmation parameter (e.g. body `{"confirm_name": "<workspace_name>"}`) and implement a 30-day soft-delete with restore. The four companion workspace-mutation endpoints (`update_workspace`, `add_member`, `update_member_role`, `remove_member`) exhibit the same default-min-role gap and are filed as their own advisories.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-g8rr-7rj2-f627
- https://github.com/MervinPraison/PraisonAI
