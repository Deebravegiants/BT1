# [H] praisonai-platform: Label endpoints' unchecked label_id/issue_id enable cross-workspace label IDOR (edit, delete, link)

## Summary
Severity: High
Advisory: GHSA-5jx9-w35f-vp65
CVE: CVE-2026-47414
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-5jx9-w35f-vp65
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Insecure Direct Object Reference. Five label endpoints — `PATCH /workspaces/{workspace_id}/labels/{label_id}`, `DELETE .../labels/{label_id}`, `POST .../issues/{issue_id}/labels/{label_id}`, `DELETE .../issues/{issue_id}/labels/{label_id}`, `GET .../issues/{issue_id}/labels` — gate access on `require_workspace_member(workspace_id)` only and pass URL-supplied `label_id` and `issue_id` straight through to `LabelService` without verifying either belongs to the workspace.
**File:** `src/praisonai-platform/praisonai_platform/services/label_service.py`, lines 35-100; route handlers at `src/praisonai-platform/praisonai_platform/api/routes/labels.py`, lines 42-106.
**Root cause:** identical pattern to the agent / issue / project / comment IDORs in this codebase: the route's `workspace_id` is used as a membership predicate but never threaded through to the service layer. `LabelService.get(label_id)` runs `session.get(IssueLabel, label_id)` with no workspace filter; `update`/`delete` inherit the gap; `add_to_issue(issue_id, label_id)` and `remove_from_issue(issue_id, label_id)` write/delete association rows without verifying either ID belongs to the membership-checked workspace; `list_for_issue(issue_id)` reads them.

## Affected Code

**File 1:** `src/praisonai-platform/praisonai_platform/services/label_service.py`, lines 35-100.

```python
class LabelService:
    ...

    async def get(self, label_id: str) -> Optional[IssueLabel]:
        return await self._session.get(IssueLabel, label_id)         # <-- BUG: no workspace_id predicate

    async def update(
        self,
        label_id: str,
        ...
    ) -> Optional[IssueLabel]:
        label = await self.get(label_id)                             # <-- inherits the gap
        ...

    async def delete(self, label_id: str) -> bool:
        label = await self.get(label_id)                             # <-- inherits the gap
        ...

    async def add_to_issue(self, issue_id: str, label_id: str) -> None:
        # writes a row in issue_label association table; no workspace check on either id

    async def remove_from_issue(self, issue_id: str, label_id: str) -> None:
        # deletes from association table; no workspace check on either id

    async def list_for_issue(self, issue_id: str) -> list[IssueLabel]:
        # reads from association table; no workspace check on issue_id
```

**File 2:** `src/praisonai-platform/praisonai_platform/api/routes/labels.py`, lines 42-106.

```python
@router.patch("/labels/{label_id}", response_model=LabelResponse)
async def update_label(workspace_id: str, label_id: str, body: LabelUpdate, ...):
    svc = LabelService(session)
    label = await svc.update(label_id, body.name, body.color)        # <-- writes any label in the DB
    ...

@router.delete("/labels/{label_id}", ...)
async def delete_label(workspace_id: str, label_id: str, ...):
    deleted = await svc.delete(label_id)                             # <-- deletes any label in the DB
    ...

@router.post("/issues/{issue_id}/labels/{label_id}", ...)
async def add_label_to_issue(workspace_id: str, issue_id: str, label_id: str, ...):
    await svc.add_to_issue(issue_id, label_id)                       # <-- attaches any label to any issue cross-workspace

@router.delete("/issues/{issue_id}/labels/{label_id}", ...)
async def remove_label_from_issue(workspace_id: str, issue_id: str, label_id: str, ...):
    await svc.remove_from_issue(issue_id, label_id)                  # <-- detaches any label from any issue cross-workspace

@router.get("/issues/{issue_id}/labels", ...)
async def list_issue_labels(workspace_id: str, issue_id: str, ...):
    labels = await svc.list_for_issue(issue_id)                      # <-- reads label assignments for any issue
```

**Why it's wrong:** the `workspace_id` URL segment is treated as a UI hint; the actual `label_id` and `issue_id` lookups query the database without a workspace constraint. The `MemberService` in this same codebase uses a composite key correctly; the label service does not. The `add_to_issue` and `remove_from_issue` paths are particularly nasty because they touch *two* unverified IDs at once: an attacker can attach a foreign workspace's label to a foreign workspace's issue (or detach the legitimate labels), corrupting both sides of an association the attacker has no business touching.

## Exploit Chain

1. Attacker registers a workspace `W_attacker` (member) and harvests a foreign-workspace `label_id` `L_T` and a foreign-workspace `issue_id` `I_T`. Both leak via `list_labels` responses (which include label IDs — but only for `W_attacker`; for the target the IDs come from issue records that include label associations, activity feeds, exported dumps, error messages). State: attacker holds `L_T` and `I_T`.
2. Attacker authenticates and sends `PATCH /workspaces/W_attacker/labels/L_T` with `{"name": "<deleted>", "color": "#000000"}`. `require_workspace_member(W_attacker, attacker)` passes. `LabelService.update(L_T, ...)` loads the foreign label and renames it. State: every issue across the foreign workspace that bears this label now displays the attacker-chosen name and colour.
3. Attacker sends `DELETE /workspaces/W_attacker/labels/L_T`. `LabelService.delete(L_T)` deletes the foreign label, dropping every issue-label association row that referenced it (cascade or orphan, depending on schema). State: foreign workspace's labels are gone or corrupted.
4. Attacker sends `POST /workspaces/W_attacker/issues/I_T/labels/L_T2` to attach foreign label `L_T2` to foreign issue `I_T`. `LabelService.add_to_issue(I_T, L_T2)` writes the association row regardless of either ID's workspace. State: the foreign issue now carries an arbitrary attacker-chosen label, which surfaces in every filter/search/board view in the foreign workspace's UI.
5. Attacker sends `DELETE /workspaces/W_attacker/issues/I_T/labels/L_legit` to strip the legitimate label off the foreign issue. State: triagers can no longer find the issue via label filters.
6. Attacker sends `GET /workspaces/W_attacker/issues/I_T/labels` to read the current label set on any foreign issue. State: the attacker fingerprints the foreign workspace's triage taxonomy.
7. Final state: with one workspace-member token plus harvested foreign IDs, the attacker rewrites and deletes other workspaces' labels, attaches/detaches arbitrary labels on other workspaces' issues, and reads triage state across the deployment.

## Security Impact

**Severity:** sec-moderate. CVSS 6.3: network attack, low complexity, low privileges, no user interaction, scope unchanged. The integrity damage is high (rename/delete of foreign labels is permanent and silent; cross-workspace label-attachment corrupts UI filters), confidentiality is low (label names are not the most sensitive field but do leak triage taxonomy), availability low (foreign workspaces may lose triage visibility into their own issues until the labels are restored).
**Attacker capability:** rename and delete any label in the multi-tenant deployment; attach any label to any issue; detach any label from any issue; list label assignments for any issue. Combined with the companion `IssueService` IDOR (separate advisory), the attacker can also modify the underlying issue, making the cross-workspace tampering very difficult to detect.
**Preconditions:** `praisonai-platform` is deployed multi-tenant; the attacker has any membership token; target IDs are known or guessable.
**Differential:** source-inspection-verified end-to-end. The asymmetry between `LabelService.list_for_workspace(workspace_id)` (correctly workspace-scoped) and `LabelService.get(label_id) / add_to_issue(issue_id, label_id)` (no workspace check) confirms the gap. With the suggested fix below, label and issue IDs that do not belong to the membership-checked workspace return 404, and the attacker cannot touch them.

## Suggested Fix

Make every single-row label lookup take the workspace predicate; verify both `issue_id` and `label_id` belong to `workspace_id` for the association routes.

```diff
--- a/src/praisonai-platform/praisonai_platform/services/label_service.py
+++ b/src/praisonai-platform/praisonai_platform/services/label_service.py
@@ -33,7 +33,12 @@ class LabelService:
         return label

-    async def get(self, label_id: str) -> Optional[IssueLabel]:
-        return await self._session.get(IssueLabel, label_id)
+    async def get(self, workspace_id: str, label_id: str) -> Optional[IssueLabel]:
+        stmt = select(IssueLabel).where(
+            IssueLabel.id == label_id,
+            IssueLabel.workspace_id == workspace_id,
+        )
+        return (await self._session.execute(stmt)).scalar_one_or_none()

-    async def add_to_issue(self, issue_id: str, label_id: str) -> None:
+    async def add_to_issue(self, workspace_id: str, issue_id: str, label_id: str) -> None:
+        # Verify both ids belong to workspace_id before writing the association row.
```

Then update the route handlers in `routes/labels.py` to thread `workspace_id` through every call. The same single-key-lookup pattern is filed separately for `AgentService`, `IssueService`, `ProjectService`, and `CommentService` — each is its own exploitable IDOR.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5jx9-w35f-vp65
- https://github.com/MervinPraison/PraisonAI
