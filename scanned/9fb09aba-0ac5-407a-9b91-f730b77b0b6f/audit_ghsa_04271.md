# [H] Gitea: OAuth2 access token scope enforcement bypass via HTTP Basic authentication

## Summary
Severity: High
Advisory: GHSA-9r5x-wg6m-x2rc
CVE: CVE-2026-28699
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-9r5x-wg6m-x2rc
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
### Summary

Gitea fails to enforce OAuth2 access token scopes when the token is submitted via HTTP Basic authentication instead of a Bearer token. An OAuth2 application granted only `read:user` can use the same token as `Authorization: Basic base64(<token>:x-oauth-basic)` and perform write actions, including modifying profiles, adding email addresses, creating repositories, and deleting repositories as the authorizing user.

### Details

**Root cause:** `services/auth/basic.go` accepts OAuth2 access tokens through the Basic auth path but does not store the token scope in the request context:

```go
// services/auth/basic.go
if uid != 0 {
    store.GetData()["LoginMethod"] = OAuth2TokenMethodName
    store.GetData()["IsApiToken"] = true   // scope is NOT set
    return u, nil
}
```

The scope enforcement middleware in `routers/api/v1/api.go` exits early when `ApiTokenScope` is absent:

```go
// routers/api/v1/api.go — tokenRequiresScopes
scope, scopeExists := ctx.Data["ApiTokenScope"].(auth_model.AccessTokenScope)
if ctx.Data["IsApiToken"] != true || !scopeExists {
    return   //<- exits without checking scope, all actions permitted
}
```

When a token arrives via Bearer, `ApiTokenScope` is populated and scope checks apply normally. When the same token arrives via Basic auth, `ApiTokenScope` is never set, so `tokenRequiresScopes` returns immediately and no scope is enforced.

**Suggested fix:** When an OAuth2 access token is accepted in `services/auth/basic.go`, populate `ApiTokenScope` in the request context identically to the Bearer-token OAuth2 path.

### PoC

1. Create an OAuth2 application in Gitea.
2. Authorize it as a normal user with scope `read:user` only.
3. Take the resulting access token and call a write endpoint both ways:

**Bearer | correctly blocked:**
```
Authorization: Bearer <token>
PATCH /api/v1/user/settings  ->  403 Forbidden
```

**Basic | bypass:**
```
Authorization: Basic base64(<token>:x-oauth-basic)
PATCH /api/v1/user/settings  ->  200 OK
```

**All verified bypass endpoints using a `read:user`-only token:**

| Endpoint | Bearer | Basic |
|---|---|---|
| `PATCH /api/v1/user/settings` | 403 | 200 |
| `POST /api/v1/user/emails` | 403 | 200 |
| `POST /api/v1/user/repos` | 403 | 200 |
| `PATCH /api/v1/repos/{owner}/{repo}` | 403 | 200 |
| `DELETE /api/v1/repos/{owner}/{repo}` | 403 | 200 |

The bypass respects the user's normal repository permissions, it does not grant access to repositories the user cannot otherwise reach, and does not escalate to admin.

### Impact

Any OAuth2 application with any restricted scope can silently operate beyond its granted permissions by switching from Bearer to Basic auth. An attacker who obtains a token (e.g. via a malicious OAuth2 app a user authorized) can:

- Modify the victim's profile and settings
- Add attacker-controlled email addresses to the victim's account
- Create repositories as the victim
- Modify or delete the victim's private repositories

The entire OAuth2 scope system is effectively bypassed for any token submitted via Basic auth.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-9r5x-wg6m-x2rc
- https://github.com/go-gitea/gitea
