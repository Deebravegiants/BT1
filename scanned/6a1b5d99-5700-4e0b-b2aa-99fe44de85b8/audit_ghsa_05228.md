# [C] praisonai-platform: Any workspace member can add arbitrary user as owner via POST /workspaces/{id}/members

## Summary
Severity: Critical
Advisory: GHSA-8g2p-pqm3-fcfh
CVE: CVE-2026-47413
CWE: CWE-269, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-8g2p-pqm3-fcfh
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Privilege escalation / cross-tenant member injection. The `POST /workspaces/{workspace_id}/members` endpoint is gated only by `require_workspace_member(workspace_id)` (default `min_role="member"`) and forwards the request body's `user_id` and `role` straight into `MemberService.add(workspace_id, user_id, role)`, which has no caller-permission check. A user with the lowest workspace privilege can add any user (including a new attacker-controlled second account, or an existing account they want to grief) as owner of the workspace.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 92-101; `services/member_service.py`, lines 26-38.
**Root cause:** `MemberService.add` validates only that `role` is in `VALID_ROLES = {"owner", "admin", "member"}` — the value, not the caller's right to assign it. The route's `Depends(require_workspace_member)` resolves to the default `min_role="member"`. So a member-level token plus one POST gives the attacker an alternate identity with owner role inside the same workspace, bypassing every owner-only operation that *would* otherwise gate them.

## Affected Code

**File 1:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 92-101.

```python
@router.post("/{workspace_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    workspace_id: str,
    body: MemberAdd,
    user: AuthIdentity = Depends(require_workspace_member),         # <-- BUG: defaults to min_role="member"
    session: AsyncSession = Depends(get_db),
):
    member_svc = MemberService(session)
    member = await member_svc.add(workspace_id, body.user_id, body.role)  # <-- writes any (user, role)
    return MemberResponse.model_validate(member)
```

**File 2:** `src/praisonai-platform/praisonai_platform/services/member_service.py`, lines 26-38.

```python
async def add(
    self,
    workspace_id: str,
    user_id: str,
    role: str = "member",
) -> Member:
    """Add a user to a workspace."""
    if role not in VALID_ROLES:                                      # only validates the value
        raise ValueError(f"Invalid role: {role}. Must be one of {VALID_ROLES}")
    member = Member(workspace_id=workspace_id, user_id=user_id, role=role)
    self._session.add(member)                                        # <-- BUG: no caller-permission check
    await self._session.flush()
    return member
```

**Why it's wrong:** workspace member management is the textbook capability that must be gated on owner role. The role hierarchy is implemented (`MemberService.has_role`, member_service.py:80-96), the dependency-tunable `min_role` parameter exists (`require_workspace_member(min_role)`, deps.py:58), but the `POST .../members` route uses neither. The `VALID_ROLES` enum check is purely cosmetic — it accepts `"owner"` from any caller because the route never asked whether the caller has the right to assign that role.

## Exploit Chain

1. Attacker registers two accounts (or recruits a member account on the target workspace `W`). Account A is an existing member of `W`; Account B is a fresh signup the attacker controls (any account on the platform — `auth/register` is open by default). State: attacker holds tokens for both A and B.
2. Attacker authenticates as Account A and POSTs `Authorization: Bearer <A_jwt>` to `POST /workspaces/W/members` with body `{"user_id": "<B_user_id>", "role": "owner"}`. State: control flow enters `add_member`.
3. `require_workspace_member(W, A)` passes (A is a member). `MemberService.add(W, B, "owner")` writes a new row `Member(workspace_id=W, user_id=B, role="owner")`. State: Account B is now a workspace-W owner.
4. Attacker switches to Account B and acts as workspace owner — change settings, add/remove members, delete the workspace, or pivot to the companion advisories' primitives. State: attacker holds owner of any workspace they had member access to, via a fresh attacker-controlled identity that the original workspace's audit logs cannot easily attribute to A.
5. Final state: with one member-level token plus one POST, the attacker plants an owner-role identity on any workspace they can reach. The same primitive lets the attacker invite a competitor or external-vendor account into the workspace as owner, exfiltrating the workspace's content under that competitor's name.

## Security Impact

**Severity:** sec-critical. CVSS 9.1: network attack, low complexity, low privileges (member tier), no user interaction, scope changed (the new owner is a different security principal), high confidentiality and integrity, no availability claim.
**Attacker capability:** with one workspace-member token plus one POST request, the attacker grants owner-tier access to any user_id on the platform. From there, full workspace control via the Account B token, plus indirect attribution: the original workspace's audit logs see "user A added user B as owner" but the audit trail cannot tell that B is attacker-controlled.
**Preconditions:** `praisonai-platform` is deployed multi-tenant; the attacker has any membership token in the target workspace; the attacker can register or knows any other user_id on the platform.
**Differential:** source-inspection-verified. The asymmetry between `MemberService.has_role` (clearly tiered) and `add_member`'s default `min_role="member"` confirms the gap. With the suggested fix below, the gate refuses the member-tier token, the elevated POST returns 403, and the second-identity owner is never created.

## Suggested Fix

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
@@ -90,11 +90,15 @@
+def _require_workspace_owner(workspace_id: str, user, session):
+    return require_workspace_member(workspace_id, user, session, min_role="owner")
+
 @router.post("/{workspace_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
 async def add_member(
     workspace_id: str,
     body: MemberAdd,
-    user: AuthIdentity = Depends(require_workspace_member),
+    user: AuthIdentity = Depends(_require_workspace_owner),
     session: AsyncSession = Depends(get_db),
 ):
     member_svc = MemberService(session)
+    if body.role == "owner" and not await member_svc.has_role(workspace_id, user.id, "owner"):
+        raise HTTPException(status_code=403, detail="Only owners can add other owners")
     member = await member_svc.add(workspace_id, body.user_id, body.role)
```

The four other workspace mutation endpoints (`update_workspace`, `delete_workspace`, `update_member_role`, `remove_member`) exhibit the same default-min-role gap and are filed as their own advisories.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-8g2p-pqm3-fcfh
- https://github.com/MervinPraison/PraisonAI
