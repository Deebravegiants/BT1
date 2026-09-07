# [M] praisonai-platform: Any workspace member can rewrite workspace name, description, and settings via PATCH /workspaces/{id}

## Summary
Severity: Medium
Advisory: GHSA-rcmc-q9rj-4wmq
CVE: CVE-2026-47411
CWE: CWE-269, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-rcmc-q9rj-4wmq
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Authorization bypass enabling workspace metadata + settings tampering. The `PATCH /workspaces/{workspace_id}` endpoint is gated only by `require_workspace_member(workspace_id)` (default `min_role="member"`). Any member can rewrite the workspace's `name`, `description`, and the `settings` JSON blob. The settings field is a free-form JSON object — depending on which downstream code reads it, this becomes a configuration-injection primitive for any setting the platform exposes there.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 63-74; `services/workspace_service.py`'s `update()` method.
**Root cause:** `Depends(require_workspace_member)` resolves to default `min_role="member"`. `WorkspaceService.update(workspace_id, name, description, settings)` writes the new fields to the workspace row without any caller-permission check. The role hierarchy (`MemberService.has_role`) is never consulted.

## Affected Code

**File:** `src/praisonai-platform/praisonai_platform/api/routes/workspaces.py`, lines 63-74.

```python
@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    body: WorkspaceUpdate,
    user: AuthIdentity = Depends(require_workspace_member),         # <-- BUG: defaults to min_role="member"
    session: AsyncSession = Depends(get_db),
):
    ws_svc = WorkspaceService(session)
    ws = await ws_svc.update(workspace_id, body.name, body.description, body.settings)  # <-- writes any value
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceResponse.model_validate(ws)
```

**Why it's wrong:** workspace name and settings are owner-tier fields. Renaming the workspace to a profanity is a low-impact griefing vector; rewriting the JSON `settings` blob is potentially a much higher-impact configuration injection (depending on what fields downstream code reads from `settings`, the attacker may flip feature flags, redirect webhook URLs, change LLM provider keys for shared configs, disable audit logging, etc.). The `require_workspace_member(min_role)` parameter is implemented and unused. This endpoint should require owner.

## Exploit Chain

1. Attacker is a member of workspace `W` with role "member". State: attacker holds JWT.
2. Attacker sends `PATCH /workspaces/W` with `Authorization: Bearer <attacker_jwt>` and body `{"name": "Compromised", "description": "Owned by attacker", "settings": {"allow_public_invite": true, "ai_provider_url": "https://attacker.example/v1"}}`. State: control flow enters `update_workspace`.
3. `require_workspace_member(W, attacker)` passes. `WorkspaceService.update(W, ...)` writes the three fields. State: workspace `W` now has attacker-chosen name, description, and settings.
4. The settings JSON is read by any downstream code that consults workspace settings (LLM proxying, invite flows, webhook routing). If the deployment uses settings-keyed configuration overrides, those overrides now point at attacker-controlled endpoints.
5. Final state: with one member-level token plus one PATCH, the attacker rewrites the workspace's metadata and settings, with effects ranging from cosmetic (rename) to substantive (settings-keyed config injection).

## Security Impact

**Severity:** sec-moderate. CVSS 6.5: network attack, low complexity, low privileges, no user interaction, scope unchanged, no confidentiality directly (though settings rewrites may enable indirect data exfiltration via attacker-pointed integration URLs), high integrity, no availability claim.
**Attacker capability:** rewrite any workspace's name, description, and settings JSON. The actual blast radius depends on what fields the deployment reads from `settings` — but that field is documented as a free-form JSON blob, so any future configuration the platform adds there becomes attacker-tunable.
**Preconditions:** `praisonai-platform` is deployed multi-tenant; attacker has any membership token in the target workspace.
**Differential:** source-inspection-verified. With the suggested fix below, member-tier tokens fail the gate and the metadata rewrite is rejected with 403.

## Suggested Fix

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/workspaces.py
@@ -63,11 +63,11 @@
 @router.patch("/{workspace_id}", response_model=WorkspaceResponse)
 async def update_workspace(
     workspace_id: str,
     body: WorkspaceUpdate,
-    user: AuthIdentity = Depends(require_workspace_member),
+    user: AuthIdentity = Depends(_require_workspace_owner),  # see member-update-role advisory for helper
     session: AsyncSession = Depends(get_db),
 ):
     ws_svc = WorkspaceService(session)
     ws = await ws_svc.update(workspace_id, body.name, body.description, body.settings)
     if ws is None:
         raise HTTPException(status_code=404, detail="Workspace not found")
     return WorkspaceResponse.model_validate(ws)
```

Defence-in-depth: validate the keys allowed in `body.settings` against an allowlist so the field cannot become an arbitrary config-injection primitive even for owners. The four companion workspace-mutation endpoints (`add_member`, `update_member_role`, `remove_member`, `delete_workspace`) exhibit the same default-min-role gap and are filed as their own advisories.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-rcmc-q9rj-4wmq
- https://github.com/MervinPraison/PraisonAI
