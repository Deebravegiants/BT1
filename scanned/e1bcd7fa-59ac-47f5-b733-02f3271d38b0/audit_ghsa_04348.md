# [H] praisonai-platform: Project endpoints accept any project_id without workspace ownership check, cross-workspace read/update/delete IDOR

## Summary
Severity: High
Advisory: GHSA-943m-6wx2-rc2j
CVE: CVE-2026-47418
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-943m-6wx2-rc2j
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Insecure Direct Object Reference. The project CRUD endpoints (`GET / PATCH / DELETE /workspaces/{workspace_id}/projects/{project_id}` and `GET .../{project_id}/stats`) gate access on `require_workspace_member(workspace_id)` only, then resolve `project_id` through `ProjectService.get(project_id)` / `update(project_id, ...)` / `delete(project_id)` / `get_stats(project_id)`. None of these calls thread `workspace_id` through to constrain the lookup. A user who is a member of any workspace `W1` can read, modify, delete, or read stats for projects that belong to a different workspace `W2`.
**File:** `src/praisonai-platform/praisonai_platform/services/project_service.py`, lines 47-108; route handlers at `src/praisonai-platform/praisonai_platform/api/routes/projects.py`, lines 51-108.
**Root cause:** identical to the agent and issue IDORs in this codebase. The route accepts `workspace_id` from URL, uses it solely for the membership gate, then calls `ProjectService.get(project_id)` which is `session.get(Project, project_id)` — a primary-key-only lookup with no `workspace_id` predicate. `update` and `delete` call `self.get(project_id)` first, inheriting the gap. `get_stats` likewise has no workspace check.

## Affected Code

**File 1:** `src/praisonai-platform/praisonai_platform/services/project_service.py`, lines 47-108.

```python
class ProjectService:
    ...

    async def get(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        return await self._session.get(Project, project_id)         # <-- BUG: no workspace_id predicate

    async def update(
        self,
        project_id: str,
        ...
    ) -> Optional[Project]:
        project = await self.get(project_id)                        # <-- inherits the gap
        ...

    async def delete(self, project_id: str) -> bool:
        project = await self.get(project_id)                        # <-- inherits the gap
        ...

    async def get_stats(self, project_id: str) -> dict:
        ...                                                          # <-- also no workspace check; returns issue counts for any project
```

**File 2:** `src/praisonai-platform/praisonai_platform/api/routes/projects.py`, lines 51-108.

```python
@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    workspace_id: str,
    project_id: str,
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = ProjectService(session)
    project = await svc.get(project_id)                             # <-- workspace_id never threaded through
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(...):
    svc = ProjectService(session)
    project = await svc.update(project_id, title=body.title, ...)   # <-- writes to any project in the DB

@router.delete("/{project_id}", ...)
async def delete_project(...):
    deleted = await svc.delete(project_id)                          # <-- deletes any project in the DB

@router.get("/{project_id}/stats")
async def project_stats(...):
    return await svc.get_stats(project_id)                          # <-- returns stats for any project in the DB
```

**Why it's wrong:** `workspace_id` from the route is treated as a UI hint (gates "are you in some workspace W?") rather than an authoritative predicate (should also gate "is the project you are addressing actually inside W?"). The `MemberService` in this same codebase uses a composite `(workspace_id, user_id)` key and demonstrates the safe pattern; the project service simply did not apply it.

## Exploit Chain

1. Attacker registers a workspace `W_attacker` (where they are a member) and harvests a target project UUID `P_T`. Project IDs leak through the activity feed (`act_svc.log` records `entity_id`), issue records (every issue carries `project_id`), webhook payloads, error messages, exported issue dumps, or operator screenshots. State: attacker holds `P_T`.
2. Attacker authenticates and sends `GET /workspaces/W_attacker/projects/P_T`. `require_workspace_member(W_attacker, attacker)` passes. State: control flow enters `get_project` with `workspace_id=W_attacker, project_id=P_T`.
3. `ProjectService.get(P_T)` runs `session.get(Project, "P_T")`, which is `SELECT * FROM projects WHERE id = 'P_T' LIMIT 1` with no `workspace_id` filter. The row is returned: `title`, `description` (often the project's confidential roadmap), `status`, `lead_type`, `lead_id`, `icon`, `created_at`, `workspace_id` (the foreign workspace's UUID is itself disclosed). State: response body is the JSON-serialised foreign project.
4. Attacker repeats with `PATCH /workspaces/W_attacker/projects/P_T` and `{"title": "<reset>", "description": "<wiped>", "status": "archived"}`. `update_project` calls `svc.update(P_T, ...)` and mutates the foreign row. State: target project is silently re-titled, re-described, and archived.
5. Attacker calls `DELETE /workspaces/W_attacker/projects/P_T` to delete the foreign project entirely. State: target project is gone (every issue still referencing it now has a dangling `project_id`).
6. Attacker calls `GET /workspaces/W_attacker/projects/P_T/stats` to read aggregate issue counts (open/closed/in-progress) for the foreign project — useful for competitive intelligence even when full-issue read is not possible.
7. Final state: any attacker with one workspace-member token can enumerate, exfiltrate, rewrite, and delete every project in the multi-tenant deployment given the project UUIDs.

## Security Impact

**Severity:** sec-high. CVSS: network attack, low complexity, low privileges, no user interaction, scope unchanged, high confidentiality (project content + cross-workspace metadata via the leaked `workspace_id` field), high integrity (arbitrary writes / deletes), no availability claim (issue rows survive parent-project deletion).
**Attacker capability:** read, edit, archive, delete, and stats-fingerprint any project in the multi-tenant deployment given the project UUID. Beyond plain content disclosure, the response also includes `workspace_id`, allowing the attacker to map the deployment's workspace topology (which workspaces exist, which projects each owns).
**Preconditions:** `praisonai-platform` is deployed multi-tenant; the attacker has any membership token; the target project's UUID is known or guessable.
**Differential:** source-inspection-verified end-to-end. The asymmetry between `ProjectService.get(project_id)` (no workspace check) and `MemberService.get(workspace_id, user_id)` (composite key check) confirms the gap. With the suggested fix below, `ProjectService.get(workspace_id, project_id)` returns `None` for foreign-workspace projects and the route handler returns 404.

## Suggested Fix

Same shape as the companion agent and issue advisories. Make the resource-lookup query include the workspace predicate; treat foreign-workspace rows as 404.

```diff
--- a/src/praisonai-platform/praisonai_platform/services/project_service.py
+++ b/src/praisonai-platform/praisonai_platform/services/project_service.py
@@ -45,9 +45,12 @@ class ProjectService:
         await self._session.flush()
         return project

-    async def get(self, project_id: str) -> Optional[Project]:
-        """Get project by ID."""
-        return await self._session.get(Project, project_id)
+    async def get(self, workspace_id: str, project_id: str) -> Optional[Project]:
+        """Get project by ID, scoped to a workspace."""
+        stmt = select(Project).where(
+            Project.id == project_id, Project.workspace_id == workspace_id
+        )
+        return (await self._session.execute(stmt)).scalar_one_or_none()

     async def update(
         self,
+        workspace_id: str,
         project_id: str,
         ...
     ) -> Optional[Project]:
-        project = await self.get(project_id)
+        project = await self.get(workspace_id, project_id)

-    async def delete(self, project_id: str) -> bool:
+    async def delete(self, workspace_id: str, project_id: str) -> bool:
-        project = await self.get(project_id)
+        project = await self.get(workspace_id, project_id)

-    async def get_stats(self, project_id: str) -> dict:
+    async def get_stats(self, workspace_id: str, project_id: str) -> dict:
+        # Also constrain the underlying issue counts query by workspace_id.
```

Update the route handlers in `routes/projects.py` to thread `workspace_id` through every call. The same single-key-lookup pattern is filed separately for `AgentService`, `IssueService`, `CommentService`, and `LabelService`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-943m-6wx2-rc2j
- https://github.com/MervinPraison/PraisonAI
