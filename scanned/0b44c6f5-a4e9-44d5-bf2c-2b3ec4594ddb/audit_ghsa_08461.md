# [H] ech0's acess tokens with expiry=never cannot be revoked: logout panics, delete does not blacklist JTI

## Summary
Severity: High
Advisory: GHSA-fpw6-hrg5-q5x5
CWE: CWE-613, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-fpw6-hrg5-q5x5
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <1.4.8-0.20260503041146-eab62379c795

## Details
## Summary

Access tokens created with the "never expire" option have no `exp` JWT claim. Three independent revocation mechanisms fail for this token type. Logout at `internal/handler/auth/auth.go:154` and `:163` dereferences `claims.ExpiresAt.Time`, panicking on the nil field so the token never hits the blacklist. `RevokeToken` at `internal/repository/auth/auth.go:45-50` skips when `remainTTL <= 0`. The admin's "Delete token" panel action at `internal/service/setting/access_token_service.go:183-185` removes the database record but does not call `RevokeToken` to blacklist the JTI. Once a never-expire token leaks, the JWT stays cryptographically valid until the admin rotates the signing key across the entire instance.

## Details

Creation path at `internal/util/jwt/jwt.go:103-105`:

```go
// expiry = 0 表示永不过期
if expiry > 0 {
    claims.ExpiresAt = jwt.NewNumericDate(time.Now().UTC().Add(time.Duration(expiry) * time.Second))
}
```

For `NEVER_EXPIRY`, `expiry = 0` and the conditional skips. The resulting JWT has no `exp` claim. The middleware at `internal/middleware/auth.go` accepts it; the `jwt/v5` parser does not require `exp` by default.

Failure mode 1, logout panic at `internal/handler/auth/auth.go:163`:

```go
// Refresh-token revocation at line 154 (safe in practice: refresh tokens always have exp).
// Access-token revocation, same pattern, at line 163 (the bug):
if claims, err := jwtUtil.ParseToken(authHeader[7:]); err == nil && claims.ID != "" {
    remaining := time.Until(claims.ExpiresAt.Time)  // nil deref when ExpiresAt is nil
    h.authService.RevokeToken(claims.ID, remaining)
}
```

For a never-expire access token, `claims.ExpiresAt` is nil. `claims.ExpiresAt.Time` panics. Gin's Recovery middleware catches it and returns HTTP 500; the JTI never reaches `RevokeToken`. Line 154 shares the same pattern against refresh tokens, but refresh tokens are always issued with an expiry so the nil dereference does not fire there in practice.

Failure mode 2, `RevokeToken` skip at `internal/repository/auth/auth.go:45-50`:

```go
func (authRepository *AuthRepository) RevokeToken(jti string, remainTTL time.Duration) {
    if jti == "" || remainTTL <= 0 {
        return
    }
    authRepository.cache.SetWithTTL(fmt.Sprintf("%s%s", blacklistPrefix, jti), true, 1, remainTTL)
}
```

Even if the logout path were patched to handle nil `ExpiresAt`, a caller computing `remainTTL = 0` would still skip the blacklist write.

Failure mode 3, admin delete at `internal/service/setting/access_token_service.go:183-185`:

```go
return settingService.transactor.Run(ctx, func(txCtx context.Context) error {
    return settingService.settingRepository.DeleteAccessTokenByID(txCtx, id)
})
```

Deletion removes the token's metadata row from the database. No call to `RevokeToken`, no write to the JTI blacklist. The JWT continues to validate because the signature is still authentic and the middleware does not consult the metadata table.

The only way to invalidate a compromised never-expire token is to rotate `JWT_SECRET`, which invalidates every token for every user across the whole instance.

## Proof of Concept

Default install. Admin creates a never-expire access token; its revocation pathways all fail:

```python
import requests, base64, json
TARGET = "http://localhost:8300"

owner = requests.post(f"{TARGET}/api/login",
                      json={"username": "owner", "password": "owner-pw"}
                     ).json()["data"]["access_token"]

# 1) Create a never-expire access token.
r = requests.post(f"{TARGET}/api/access-tokens",
                  headers={"Authorization": f"Bearer {owner}",
                           "content-type": "application/json"},
                  json={"name": "poc-irrevocable",
                        "expiry": "never",
                        "scopes": ["profile:read"],
                        "audience": "cli"})
tok = r.json()["data"]
pad = lambda s: s + "=" * (-len(s) % 4)
payload = json.loads(base64.urlsafe_b64decode(pad(tok.split(".")[1])))
print(f"  exp claim: {payload.get('exp')}  (None = never expires)")
print(f"  jti: {payload['jti']}")

# 2) Confirm it works.
r = requests.get(f"{TARGET}/api/user", headers={"Authorization": f"Bearer {tok}"})
print(f"  token -> /api/user: HTTP {r.status_code}")

# 3) Failure mode #1 — logout panics on nil ExpiresAt.
r = requests.post(f"{TARGET}/api/auth/logout",
                  headers={"Authorization": f"Bearer {tok}"})
print(f"  logout: HTTP {r.status_code} (500 = Recovery middleware caught the panic)")

# 4) Failure mode #3 — admin delete does not blacklist the JTI.
listed = requests.get(f"{TARGET}/api/access-tokens",
                      headers={"Authorization": f"Bearer {owner}"}).json()["data"]
poc_row = next(t for t in listed if t["name"] == "poc-irrevocable")
r = requests.delete(f"{TARGET}/api/access-tokens/{poc_row['id']}",
                    headers={"Authorization": f"Bearer {owner}"})
print(f"  admin delete: HTTP {r.status_code} {r.text}")

# 5) Token should now be invalid if delete blacklisted. Test it.
r = requests.get(f"{TARGET}/api/user", headers={"Authorization": f"Bearer {tok}"})
print(f"  after delete, token -> /api/user: HTTP {r.status_code}")
print(f"  response body: {r.text[:150]}")
```

Observed on v4.5.6 in the test container:

```
exp claim: None  (None = never expires)
jti: 019daf86-6354-7c2d-9ff1-180de87667b3
token -> /api/user: HTTP 200
logout: HTTP 500 (500 = Recovery middleware caught the panic)
admin delete: HTTP 200 {"code":1,"msg":"删除访问令牌成功","data":null}
after delete, token -> /api/user: HTTP 200
response body: {"code":1,"msg":"获取用户信息成功","data":{"id":"019daf76-b5d2-7778-a90a-e943872b2946","username":"owner","email":"owner@test.local","is_admin":true,"is_owner":true,...}}
```

After the admin "deleted" the token, the same JWT string still returns the owner's profile data. The token stays valid with no path to invalidate it short of rotating `JWT_SECRET`.

## Impact

The "never expire" option is intended for CLI and integration use cases where rotating tokens is expensive. When one of those tokens leaks (configuration file committed to a public repo, developer laptop compromised, log file uploaded by mistake), the admin has no remediation that does not nuke every other user's session.

A compromised token gives the attacker:

- **Perpetual authenticated access** at whatever scopes the token holds until the JWT secret is rotated.
- **Admin's "revoke" UI button lies.** The token row disappears from the panel but the bearer keeps working. The admin believes they mitigated the incident.
- **Instance-wide blast radius on proper revocation.** The only working fix (rotate JWT_SECRET) forces every user to log in again and invalidates every other access token. Security incidents force operators into an all-or-nothing choice.

Precondition: token theft. A stolen token is the standard threat model for any long-lived credential; the point of revocation is that stolen credentials can be invalidated. Ech0 currently has no working path to do that for the "never expire" class.

## Recommended Fix

Three coordinated changes, matching the three failure modes:

1. Replace "never expire" with a very long expiry (for example 10 years) so every token has a finite `exp` claim. This removes the conditional at `jwt.go:103` entirely:

```go
if expiry == model.NEVER_EXPIRY {
    expiry = int64((10 * 365 * 24 * time.Hour).Seconds())
}
claims.ExpiresAt = jwt.NewNumericDate(time.Now().UTC().Add(time.Duration(expiry) * time.Second))
```

2. If the "never expire" semantics must be preserved, make logout handle nil `ExpiresAt` explicitly:

```go
if claims, err := jwtUtil.ParseToken(authHeader[7:]); err == nil && claims.ID != "" {
    var remaining time.Duration
    if claims.ExpiresAt != nil {
        remaining = time.Until(claims.ExpiresAt.Time)
    } else {
        remaining = 365 * 24 * time.Hour
    }
    h.authService.RevokeToken(claims.ID, remaining)
}
```

And accept non-positive TTLs in `RevokeToken` by substituting a long default.

3. Blacklist the JTI when admin deletes an access token:

```go
tok, err := settingService.settingRepository.GetAccessTokenByID(ctx, id)
if err != nil {
    return err
}
if tok.JTI != "" {
    settingService.authRepo.RevokeToken(tok.JTI, 365*24*time.Hour)
}
return settingService.transactor.Run(ctx, func(txCtx context.Context) error {
    return settingService.settingRepository.DeleteAccessTokenByID(txCtx, id)
})
```

Any two of the three changes close the gap; all three together make the revocation semantics match the admin's mental model.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-fpw6-hrg5-q5x5
- https://github.com/lin-snow/Ech0/commit/eab62379c795c3f4850a9ca938ae3f27d7171541
- https://github.com/lin-snow/Ech0
