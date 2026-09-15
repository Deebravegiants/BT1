# [H] praisonai-platform: IDOR in dependency endpoints allows cross-workspace issue linking, reading, and deletion due to missing ownership checks

## Summary
Severity: High
Advisory: GHSA-4x6r-9v57-3gqw
CVE: CVE-2026-47406
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-4x6r-9v57-3gqw
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Insecure Direct Object Reference. The dependency endpoints (`POST/GET /workspaces/{workspace_id}/issues/{issue_id}/dependencies` and `DELETE .../dependencies/{dep_id}`) gate access on `require_workspace_member(workspace_id)` only, then dispatch to `DependencyService` calls that take URL/body-supplied issue and dependency IDs without verifying any of them belong to the membership-checked workspace. Most damaging: `create_dependency` accepts `body.depends_on_issue_id` from the request body — that ID is checked against nothing — letting an attacker create a "blocks" or "related" link between any two issues anywhere in the database.
**File:** `src/praisonai-platform/praisonai_platform/api/routes/dependencies.py`, lines 22-58; `services/dependency_service.py`, lines 26-65.
**Root cause:** the same `Depends(require_workspace_member)` default-min-role pattern as the companion IDORs, plus a service layer (`DependencyService`) where every method takes raw IDs and queries them directly. `create(issue_id, depends_on_issue_id, ...)` writes a row with no workspace verification on either ID. `list_for_issue(issue_id)` returns dependencies in either direction. `delete(dep_id)` is a primary-key delete with no workspace predicate.

## Affected Code

**File 1:** `src/praisonai-platform/praisonai_platform/api/routes/dependencies.py`, lines 22-58.

```python
@router.post("/", response_model=DependencyResponse, status_code=status.HTTP_201_CREATED)
async def create_dependency(
    workspace_id: str,
    issue_id: str,
    body: DependencyCreate,
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = DependencyService(session)
    dep = await svc.create(issue_id, body.depends_on_issue_id, body.type)  # <-- BUG: neither id is workspace-checked
    return DependencyResponse.model_validate(dep)


@router.get("/", response_model=List[DependencyResponse])
async def list_dependencies(
    workspace_id: str,
    issue_id: str,
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = DependencyService(session)
    deps = await svc.list_for_issue(issue_id)                              # <-- BUG: returns dependencies for any issue
    return [DependencyResponse.model_validate(d) for d in deps]


@router.delete("/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dependency(
    workspace_id: str,
    issue_id: str,
    dep_id: str,
    user: AuthIdentity = Depends(require_workspace_member),
    session: AsyncSession = Depends(get_db),
):
    svc = DependencyService(session)
    deleted = await svc.delete(dep_id)                                     # <-- BUG: deletes any dependency by id
    if not deleted:
        raise HTTPException(status_code=404, detail="Dependency not found")
```

**File 2:** `src/praisonai-platform/praisonai_platform/services/dependency_service.py`, lines 26-65.

```python
async def create(self, issue_id: str, depends_on_issue_id: str, dep_type: str = "blocks") -> IssueDependency:
    if dep_type not in VALID_TYPES:
        raise ValueError(...)
    dep = IssueDependency(
        issue_id=issue_id,                                              # <-- accepts any
        depends_on_issue_id=depends_on_issue_id,                        # <-- accepts any (from request body)
        type=dep_type,
    )
    self._session.add(dep); await self._session.flush(); return dep

async def list_for_issue(self, issue_id: str) -> list[IssueDependency]:
    stmt = select(IssueDependency).where(
        (IssueDependency.issue_id == issue_id) | (IssueDependency.depends_on_issue_id == issue_id)
    )
    return list((await self._session.execute(stmt)).scalars().all())

async def delete(self, dep_id: str) -> bool:
    dep = await self.get(dep_id)                                        # session.get(IssueDependency, dep_id) — no workspace check
    ...
```

**Why it's wrong:** the request-body `depends_on_issue_id` is the worst part: an attacker can link any two issues across any two workspaces, polluting both workspaces' dependency graphs with attacker-chosen relationships ("blocks", "blocked_by", "related"). The triagers in the foreign workspace see their issue suddenly blocked by an unrelated foreign issue, breaking sprint planning and creating false correlation. The `delete(dep_id)` path lets an attacker remove legitimate cross-issue links between any two foreign workspaces, also disrupting their planning. The `list_for_issue` path leaks the dependency graph for any issue in the deployment.

## Exploit Chain

1. Attacker is a member of workspace `W_attacker` and harvests two foreign-workspace issue UUIDs `I1` (in `W_target1`) and `I2` (in `W_target2`). They leak via the activity feed, comment threads, error messages, exported dumps, the agent prompt history, or any other channel that ever serialises an issue ID. State: attacker holds two foreign issue UUIDs.
2. Attacker sends `POST /workspaces/W_attacker/issues/I1/dependencies` with `Authorization: Bearer <attacker_jwt>` and body `{"depends_on_issue_id": "I2", "type": "blocks"}`. State: control flow enters `create_dependency` with `issue_id=I1` (foreign), `depends_on_issue_id=I2` (foreign).
3. `require_workspace_member(W_attacker, attacker)` passes (attacker is a member of `W_attacker`). `DependencyService.create(I1, I2, "blocks")` writes a new row `IssueDependency(issue_id=I1, depends_on_issue_id=I2, type="blocks")`. State: there is now a cross-workspace dependency between two foreign issues, written by the attacker.
4. The triage UIs of `W_target1` and `W_target2` now show that the foreign issue is blocked by an unrelated issue in another workspace. Workflow rules that key off "cannot close while blocked" will refuse to let the legitimate triagers close `I1`. State: foreign workflow disrupted.
5. Attacker repeats with `GET /workspaces/W_attacker/issues/I1/dependencies` to read the dependency graph for any foreign issue (information disclosure, project relationship mapping), or with `DELETE .../{dep_id}` (after enumerating dep_ids via the list call) to strip legitimate dependencies between foreign issues, breaking blocked-by chains.
6. Final state: with one workspace-member token, the attacker reads, writes, and deletes dependencies on every issue in the multi-tenant deployment, polluting the dependency graphs of foreign workspaces.

## Security Impact

**Severity:** sec-high. CVSS 7.6: network attack, low complexity, low privileges, no user interaction, scope unchanged, high confidentiality (cross-workspace dependency graph disclosure), high integrity (cross-workspace dependency injection and deletion), no availability claim (workflow disruption is integrity, not availability).
**Attacker capability:** read any issue's dependency graph; create arbitrary "blocks" / "blocked_by" / "related" links between any two issues across any two workspaces; delete any dependency by id. The most surprising primitive is the cross-workspace LINKING — the only one of the IDORs in this codebase where a single attacker request can affect TWO foreign workspaces at once.
**Preconditions:** `praisonai-platform` is deployed multi-tenant; attacker has any membership token; foreign issue UUIDs are reachable.
**Differential:** source-inspection-verified end-to-end. The asymmetry between this service (no workspace predicate anywhere) and `MemberService.get(workspace_id, user_id)` (correctly composite-keyed) confirms the gap. With the suggested fix below, the route would resolve both the URL `issue_id` and the body `depends_on_issue_id` against `IssueService.get(workspace_id, ...)` before allowing the dependency to be written.

## Suggested Fix

Resolve every issue id (URL and body) against `workspace_id` at the route layer before dispatching. The route helper from the issue-IDOR companion advisory can be reused.

```diff
--- a/src/praisonai-platform/praisonai_platform/api/routes/dependencies.py
+++ b/src/praisonai-platform/praisonai_platform/api/routes/dependencies.py
@@ -22,11 +22,16 @@
 @router.post("/", response_model=DependencyResponse, status_code=status.HTTP_201_CREATED)
 async def create_dependency(
     workspace_id: str,
     issue_id: str,
     body: DependencyCreate,
     user: AuthIdentity = Depends(require_workspace_member),
     session: AsyncSession = Depends(get_db),
 ):
+    issue_svc = IssueService(session)
+    if await issue_svc.get(workspace_id, issue_id) is None:
+        raise HTTPException(status_code=404, detail="Issue not found")
+    if await issue_svc.get(workspace_id, body.depends_on_issue_id) is None:
+        raise HTTPException(status_code=404, detail="depends_on_issue_id not found in this workspace")
     svc = DependencyService(session)
     dep = await svc.create(issue_id, body.depends_on_issue_id, body.type)
     return DependencyResponse.model_validate(dep)
```

Apply the same `issue_svc.get(workspace_id, issue_id)` precondition to `list_dependencies` and `delete_dependency` (verifying both the issue and the dependency belong to `workspace_id`).

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-4x6r-9v57-3gqw
- https://github.com/MervinPraison/PraisonAI
