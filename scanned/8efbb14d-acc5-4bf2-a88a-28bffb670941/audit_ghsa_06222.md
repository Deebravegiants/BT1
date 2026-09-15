# [M] Vikunja has a project duplication bypasses write-permission check on the target parent project

## Summary
Severity: Medium
Advisory: GHSA-f27p-pw2p-9pr4
CVE: CVE-2026-54766
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-f27p-pw2p-9pr4
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0.21.0 <2.4.0

## Details
## Summary

The project-duplication endpoint fails to enforce write access to the target parent project. Any authenticated (non-link-share) user can duplicate a project they can read into **any** parent project on the instance, regardless of whether they have write access to that parent — injecting an attacker-owned project into another user's or team's project hierarchy.

## Details

`ProjectDuplicate.CanCreate` (`pkg/models/project_duplicate.go`) is meant to require write access to the parent the duplicate is placed under — its own comment says "Parent project exists + user has write access". The implementation does neither correctly:

```go
func (pd *ProjectDuplicate) CanCreate(s *xorm.Session, a web.Auth) (canCreate bool, err error) {
    pd.Project = &Project{ID: pd.ProjectID}
    canRead, _, err := pd.Project.CanRead(s, a)
    if err != nil || !canRead {
        return canRead, err
    }
    if pd.ParentProjectID == 0 {
        return canRead, err
    }
    // Parent project exists + user has write access to is (-> can create new projects)
    parent := &Project{ID: pd.ParentProjectID}
    return parent.CanCreate(s, a)   // <-- bug
}
```

Two defects compound here:

1. **Wrong permission method.** It calls `parent.CanCreate` ("may I create *this* project?") instead of `parent.CanWrite` ("may I create children *inside* this project?"). The latter is what the normal create path uses — `POST /projects` with a `parent_project_id` enforces `parent.CanWrite` via `Project.CanCreate` (`pkg/models/project_permissions.go:196-199`).

2. **Unhydrated struct.** `parent` is constructed as `&Project{ID: pd.ParentProjectID}` and never loaded from the database, so its in-memory `ParentProjectID` is always `0`. Inside `Project.CanCreate` the only branch that performs any permission check is `if p.ParentProjectID != 0 { return parent.CanWrite(...) }` — which therefore never executes. Control falls through to the link-share check and then `return true, nil`. The result is `true` for any authenticated non-link-share user, for any `ParentProjectID`.

Nothing downstream re-checks: `ProjectDuplicate.Create` → `CreateProject` → `checkProjectBeforeUpdateOrDelete` (`pkg/models/project.go:954`) validates only that the parent exists, is not a pseudo-project, and introduces no cycle — no authorization.

## Impact

An authenticated user can:

- Duplicate any project they can read (including their own) and attach the copy as a child of **any** parent project ID on the instance, with no write access to that parent.
- Inject an attacker-owned project into other users'/teams' project trees. The duplicate is owned by the attacker but appears inside the victim's hierarchy; members of the victim parent see it, and because Vikunja propagates parent access down the tree, they may inherit access to the injected project — enabling content injection / spam / phishing inside another tenant's workspace.

This is a bypass of the same parent-write guard that the ordinary create path enforces, so the duplicate route is an authorization hole for an operation that is otherwise correctly gated. The endpoint requires authentication; it does not expose or modify the victim's existing project data (the source is attacker-readable), so the impact is an integrity / access-control violation rather than confidentiality.

## Proof of Concept

1. As user A, create or have read access to any project `S` (e.g. id 100).
2. Identify a parent project `P` (e.g. id 5) owned by user B, to which A has **no** access.
3. Call `PUT /api/v1/projects/100/duplicate` with body `{"parent_project_id": 5}`.
4. The request succeeds (201). A new project owned by A is created as a child of B's project 5, despite A having no write access to it. The equivalent `POST /api/v1/projects` with `parent_project_id: 5` would be correctly rejected with 403.

## Affected versions

Introduced with the namespace→project migration (commit `fef253312`, first released in v0.21.0) and present through the latest release (v2.3.0). The shared model also backs the new `/api/v2` duplication route under review, so any v2 release would inherit the same flaw unless fixed in the model.

## Recommended Fix

In `ProjectDuplicate.CanCreate`, check write access to the parent directly:

```go
parent := &Project{ID: pd.ParentProjectID}
return parent.CanWrite(s, a)
```

`Project.CanWrite` loads the project from the database and evaluates real permissions, fixing both the wrong-method and the unhydrated-struct defects at once and matching the documented contract. (It also rejects archived parents, which is desirable.)

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-f27p-pw2p-9pr4
- https://github.com/go-vikunja/vikunja/pull/3239
- https://github.com/go-vikunja/vikunja/commit/d911caaa11c748c3abc6b98b3189afea2677bcb0
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.4.0
