# [M] Gogs Vulnerable to Privilege Escalation via Collaboration Access Mode Validation

## Summary
Severity: Medium
Advisory: GHSA-4565-r4x7-hg8j
CVE: CVE-2026-52804
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-4565-r4x7-hg8j
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

A repository admin collaborator can escalate their privileges to owner-level access by exploiting an off-by-one error in the `ChangeCollaborationAccessMode` function.

## Vulnerable Code

In `internal/database/repo_collaboration.go`, line 129:

```go
func (r *Repository) ChangeCollaborationAccessMode(userID int64, mode AccessMode) error {
    // Discard invalid input
    if mode <= AccessModeNone || mode > AccessModeOwner {
        return nil
    }
```

`AccessModeOwner` has value 4. The check `mode > AccessModeOwner` evaluates to `4 > 4 = false`, allowing `AccessModeOwner` to pass through. The correct check should be `mode >= AccessModeOwner`.

The web route at `internal/route/repo/setting.go:413-416` takes the mode as a raw integer from query parameters:

```go
func ChangeCollaborationAccessMode(c *context.Context) {
    if err := c.Repo.Repository.ChangeCollaborationAccessMode(
        c.QueryInt64("uid"),
        database.AccessMode(c.QueryInt("mode"))); err != nil {
```

This allows an admin collaborator to POST `mode=4` and escalate to owner.

## Impact

A repository admin collaborator (AccessModeAdmin = 3) can escalate to owner-level access (AccessModeOwner = 4), gaining the ability to:
- **Delete the repository**
- **Transfer repository ownership** to another user
- **Erase wiki data**
- Perform all other owner-only operations

The `access` table is also updated (line 181), so the escalated permissions persist across sessions.

## Contrast

The API route at `internal/route/api/v1/repo_collaborators.go:46` uses `ParseAccessMode()` which only returns Read, Write, or Admin - never Owner. The API endpoint is not affected.

## Steps to Reproduce

1. User A creates a private repository
2. User A adds User B as a collaborator with **Admin** access (mode=3)
3. User B logs in and navigates to the repository settings collaboration page
4. User B sends a POST request:
   ```
   POST /{owner}/{repo}/settings/collaboration/access_mode?uid={B_uid}&mode=4
   ```
5. User B now has **Owner** access - the "Danger Zone" section appears with "Delete This Repository" and "Transfer Ownership" buttons

## Suggested Fix

Change the validation in `internal/database/repo_collaboration.go` line 129 from:
```go
if mode <= AccessModeNone || mode > AccessModeOwner {
```
to:
```go
if mode <= AccessModeNone || mode >= AccessModeOwner {
```

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-4565-r4x7-hg8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-52804
- https://github.com/gogs/gogs/pull/8227
- https://github.com/gogs/gogs/commit/1fdc9cc28e159135cfa4d6b11ecd5daa0f8ce22b
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
