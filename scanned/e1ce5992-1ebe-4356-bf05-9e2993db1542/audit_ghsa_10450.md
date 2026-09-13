# [M] Vikunja: Link Share JWT tokens remain valid for 72 hours after share deletion or permission downgrade

## Summary
Severity: Medium
Advisory: GHSA-96q5-xm3p-7m84
CVE: CVE-2026-35594
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-96q5-xm3p-7m84
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Title
Link Share JWT tokens remain valid for 72 hours after share deletion or permission downgrade

## Description

Vikunja's link share authentication constructs authorization objects entirely from JWT claims without any server-side database validation. When a project owner deletes a link share or downgrades its permissions, all previously issued JWTs continue to grant the **original** permission level for up to **72 hours** (the default `service.jwtttl`).

`GetLinkShareFromClaims` at `pkg/models/link_sharing.go` lines 88-119 performs **zero database queries** — it builds the `LinkSharing` struct purely from JWT claim values (`id`, `hash`, `project_id`, `permission`, `sharedByID`). This struct is passed directly to permission checks:

| Function | File | Lines | DB queries |
|----------|------|-------|------------|
| `GetLinkShareFromClaims` | `link_sharing.go` | 88-119 | 0 |
| `Project.CanRead` (link share) | `project_permissions.go` | 105-108 | 0 |
| `Project.CanWrite` (link share) | `project_permissions.go` | 50-53 | 0 |
| `Project.IsAdmin` (link share) | `project_permissions.go` | 192-194 | 0 |

**Contrast with user tokens:** User JWTs use a 10-minute TTL (`ServiceJWTTTLShort`) with `sid` claim and server-side sessions enabling revocation. Link share JWTs use a 72-hour TTL (`ServiceJWTTTL`) with no `sid`, no server-side session, and no refresh mechanism.

**Permalink:**
- `GetLinkShareFromClaims`: `pkg/models/link_sharing.go:88-119`
- `NewLinkShareJWTAuthtoken`: `pkg/modules/auth/auth.go:141-160`
- Permission checks: `pkg/models/project_permissions.go:50-53, 105-108, 192-194`
- TTL defaults: `pkg/config/config.go:337-339`

### PoC

```bash
# 1. Create an Admin-level link share on project 42
curl -X PUT "https://vikunja.example.com/api/v1/projects/42/shares" \
  -H "Authorization: Bearer <owner-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"permission": 2}'
# Response: {"id": 5, "hash": "abc123", ...}

# 2. Obtain link share JWT (72h TTL, no sid claim)
curl -X POST "https://vikunja.example.com/api/v1/shares/abc123/auth"
# Response: {"token": "<link-share-jwt>"}

# 3. Delete the link share
curl -X DELETE "https://vikunja.example.com/api/v1/projects/42/shares/5" \
  -H "Authorization: Bearer <owner-jwt>"
# 200 OK — share row removed from database

# 4. Use the deleted share's JWT — STILL WORKS for up to 72 hours
curl -X GET "https://vikunja.example.com/api/v1/projects/42/tasks" \
  -H "Authorization: Bearer <link-share-jwt>"
# 200 OK — full task list returned with Admin permissions

# 5. Permission downgrade variant:
# Delete Admin share → create Read-only share → old JWT still has Admin access
```

### Impact

- Revoked link shares remain functional for up to 72 hours (default TTL)
- Project owners cannot respond to security events (leaked URLs, access revocation) in real time
- Permission downgrades have no effect on outstanding tokens
- Scope: single project per token, severity scales with permission level (Admin > Write > Read)

### Fix

Add database validation in `GetLinkShareFromClaims`:

```go
func GetLinkShareFromClaims(claims jwt.MapClaims) (share *LinkSharing, err error) {
    id, is := claims["id"].(float64)
    if !is {
        return nil, &ErrLinkShareTokenInvalid{}
    }
    // Validate against database
    s := db.NewSession()
    defer s.Close()
    share, err = GetLinkShareByID(s, int64(id))
    if err != nil {
        return nil, err  // Share was deleted
    }
    // Verify permission not downgraded
    claimedPermission := Permission(claims["permission"].(float64))
    if share.Permission < claimedPermission {
        return nil, &ErrLinkShareTokenInvalid{}
    }
    return share, nil
}
```

Alternatives: shorter TTL with refresh mechanism, token blocklist, or session tracking matching user token pattern.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-96q5-xm3p-7m84
- https://nvd.nist.gov/vuln/detail/CVE-2026-35594
- https://github.com/go-vikunja/vikunja/pull/2581
- https://github.com/go-vikunja/vikunja/commit/379d8a5c19334ffe4846003f590e202c31a75479
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
