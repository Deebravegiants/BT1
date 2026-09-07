# [M] Vikunja has a Link Share Delete IDOR — Missing Project Ownership Check Allows Cross-Project Link Share Deletion

## Summary
Severity: Medium
Advisory: GHSA-f95f-77jx-fcjc
CVE: CVE-2026-33700
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-f95f-77jx-fcjc
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

The `DELETE /api/v1/projects/:project/shares/:share` endpoint does not verify that the link share belongs to the project specified in the URL. An attacker with admin access to any project can delete link shares from other projects by providing their own project ID combined with the target share ID.

## Details

The permission check in `canDoLinkShare` (`pkg/models/link_sharing_permissions.go:53-70`) validates admin access on the project from the `:project` URL parameter. However, the `Delete` method at `pkg/models/link_sharing.go:305` queries only `WHERE id = ?` using the share ID, without verifying it belongs to the URL-specified project:

```go
func (share *LinkSharing) Delete(s *xorm.Session, _ web.Auth) (err error) {
    _, err = s.Where("id = ?", share.ID).Delete(share)
    return
}
```

This is the same vulnerability class as GHSA-jfmm-mjcp-8wq2 (task attachment IDOR) and the fixed GHSA-mr3j-p26x-72x4 (task comment IDOR).

Additionally, `ReadOne` at line 203 has the same pattern (`WHERE id = ?` only), though it is not currently exploitable because `CanRead` fails first due to an unrelated issue with the hash parameter binding.

## Impact

An authenticated user with admin access to any project can:
- Delete link shares belonging to any other project in the system
- Disrupt collaboration by removing shared access links
- Link share IDs are sequential integers, making enumeration trivial

## Reproduction

1. User A creates Project A and a link share on it (share ID = X)
2. User B creates Project B (gaining admin access)
3. User B calls `DELETE /api/v1/projects/{projectB_id}/shares/{X}`
4. The permission check passes (User B is admin on Project B)
5. The delete executes `WHERE id = X` — deleting User A's link share

## Recommended Fix

Change `Delete` at `pkg/models/link_sharing.go:305` to:

```go
_, err = s.Where("id = ? AND project_id = ?", share.ID, share.ProjectID).Delete(share)
```

Also fix `ReadOne` at line 203 as defense in depth.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-f95f-77jx-fcjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33700
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
