# [H] praisonai-platform: Missing authorization on member removal enables full workspace takeover by any user regardless of role

## Summary
Severity: High
Advisory: GHSA-w388-2392-px73
CVE: CVE-2026-47409
CWE: CWE-269, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-w388-2392-px73
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Authorization bypass enabling owner lockout. The `DELETE /workspaces/{workspace_id}/members/{user_id}` endpoint is gated only by `require_workspace_member(workspace_id)` (default `min_role="member"`). Any member can remove any other member, including the workspace owner, using a single DELETE. There is no caller-role check, no target-role check, no "cannot remove last owner" guard.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 130-140; `services/member_service.py`, lines 71-78.
**Root cause:** `MemberService.remove(workspace_id, user_id)` performs the deletion without any caller-permission check or owner-protection logic. The route accepts the URL-supplied `user_id` and dispatches it straight through. The role hierarchy (`MemberService.has_role`) is implemented but never invoked here. A member-tier attacker can issue `DELETE .../members/<owner_user_id>` and immediately lock the legitimate owner out of the workspace.

## Affected Code

**File 1:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 130-140.

```python
@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: str,
    user_id: str,
    user: AuthIdentity = Depends(require_workspace_member),         # <-- BUG: defaults to min_role="member"
    session: AsyncSession = Depends(get_db),
):
    member_svc = MemberService(session)
    removed = await member_svc.remove(workspace_id, user_id)        # <-- removes any member, including owner
    if not removed:
        raise HTTPException(status_code=404, detail="Member not found")
```

**File 2:** `src/praisonai-platform/praisonai_platform/services/member_service.py`, lines 71-78.

```python
async def remove(self, workspace_id: str, user_id: str) -> bool:
    """Remove a member from a workspace."""
    member = await self.get(workspace_id, user_id)
    if member is None:
        return False
    await self._session.delete(member)                               # <-- BUG: no caller-role check, no last-owner protection
    await self._session.flush()
    return True
```

**Why it's wrong:** member-removal is the textbook capability that must be gated on owner role. Removing the workspace owner is a permanent denial-of-service against the legitimate owner unless another owner exists. There must be (a) a caller min-role gate of "owner" or "admin", (b) a check that prevents removing a member whose role is higher than the caller's, and (c) a check that the workspace is left with at least one owner. None of these exist.

## Exploit Chain

1. Attacker is a member of workspace `W` with role "member". State: attacker holds JWT.
2. Attacker enumerates the workspace owner's `user_id` via `GET /workspaces/W/members` (list_members has the same default-member gate, separate finding). Owner UUID `O_id` is now known. State: attacker holds `O_id`.
3. Attacker sends `DELETE /workspaces/W/members/O_id` with `Authorization: Bearer <attacker_jwt>`. State: control flow enters `remove_member`.
4. `require_workspace_member(W, attacker)` passes (attacker is a member). `MemberService.remove(W, O_id)` deletes the owner's member row. State: `Member(workspace_id=W, user_id=O_id, role="owner")` is gone.
5. Owner attempts `GET /workspaces/W/...` and `require_workspace_member(W, O_id)` returns 403. State: legitimate owner is now locked out of their own workspace.
6. Combined with the `update_member_role` companion advisory, the attacker first promotes themselves to owner, then removes the legitimate owner, then has uncontested control. Combined with `delete_workspace`, the attacker wipes the workspace after kicking the owner.
7. Final state: with one member-level token, the attacker locks the legitimate owner out of their own workspace permanently. The owner has no recourse other than database-level admin intervention.

## Security Impact

**Severity:** sec-high. CVSS 8.1: network attack, low complexity, low privileges, no user interaction, scope unchanged, no confidentiality, high integrity (membership table corrupted), high availability (legitimate owner cannot access their own workspace).
**Attacker capability:** with one workspace-member token plus one DELETE request, the attacker permanently locks any other member (including the workspace owner) out of the workspace.
**Preconditions:** `praisonai-platform` is deployed multi-tenant; attacker has any membership token; owner's user_id is reachable via the (unauthenticated-for-member) `list_members` endpoint.
**Differential:** source-inspection-verified. The asymmetry between `require_workspace_member`'s tunable `min_role` parameter and this endpoint's use of the default value confirms the gap. With the suggested fix below, member-tier tokens fail the gate, and removing the workspace's last owner triggers the additional guard.

## Suggested Fix

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
@@ -130,11 +130,21 @@
 @router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
 async def remove_member(
     workspace_id: str,
     user_id: str,
-    user: AuthIdentity = Depends(require_workspace_member),
+    user: AuthIdentity = Depends(_require_workspace_owner),
     session: AsyncSession = Depends(get_db),
 ):
     member_svc = MemberService(session)
+    target = await member_svc.get(workspace_id, user_id)
+    if target is not None and target.role == "owner":
+        # Refuse to remove the last owner.
+        owners = [m for m in await member_svc.list_members(workspace_id) if m.role == "owner"]
+        if len(owners) <= 1:
+            raise HTTPException(status_code=409, detail="Cannot remove the last workspace owner")
     removed = await member_svc.remove(workspace_id, user_id)
     if not removed:
         raise HTTPException(status_code=404, detail="Member not found")
```

The four companion workspace-mutation endpoints exhibit the same default-min-role gap and are filed as their own advisories.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-w388-2392-px73
- https://github.com/MervinPraison/PraisonAI
