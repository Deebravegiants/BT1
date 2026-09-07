# [M] Vikunja read-only users can delete project background images via broken object-level authorization

## Summary
Severity: Medium
Advisory: GHSA-564f-wx8x-878h
CVE: CVE-2026-33312
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-564f-wx8x-878h
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0.20.2 <2.2.0

## Details
## Summary

The `DELETE /api/v1/projects/:project/background` endpoint checks `CanRead` permission instead of `CanUpdate`, allowing any user with read-only access to a project to permanently delete its background image.

## Details

The `RemoveProjectBackground` handler (`pkg/modules/background/handler/background.go`) reuses `checkProjectBackgroundRights`, a helper originally written for the read-only `GetProjectBackground` endpoint. This helper only verifies `CanRead` permission. In contrast, the handler for *setting* a background (`setBackgroundPreparations`) correctly checks `CanUpdate`.

As a result, destructive write operations (deleting the background file from storage and clearing the project's `background_file_id` and `background_blur_hash` fields) are gated behind a read-only permission check.

## Impact

A user with read-only access to a project — via direct sharing, team membership, link share tokens with read permission, or read-scoped API tokens — can permanently delete the project's background image. The background file is removed from storage and cannot be recovered. This constitutes unauthorized data destruction.

## Reproduction

1. User A creates a project and sets a background image.
2. User A shares the project with User B with **read-only** permission.
3. User B sends: `DELETE /api/v1/projects/{project_id}/background` with a valid auth token.
4. The request succeeds. The background image is permanently deleted.

## References

- `pkg/modules/background/handler/background.go` — `RemoveProjectBackground` (line 416), `checkProjectBackgroundRights` (line 304), `setBackgroundPreparations` (line 106)
- `pkg/routes/routes.go` line 665 — route registration

## Credits

This vulnerability was found using [GitHub Security Lab Taskflows](https://github.com/GitHubSecurityLab/seclab-taskflows).

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-564f-wx8x-878h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33312
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.0-was-released
