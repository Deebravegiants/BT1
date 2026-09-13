# [H] Tinyauth has OAuth account confusion via shared mutable state on singleton service instances

## Summary
Severity: High
Advisory: GHSA-9q5m-jfc4-wc92
CVE: CVE-2026-33544
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-9q5m-jfc4-wc92
Type: github-advisory

## Affected
- Go: `github.com/steveiliop56/tinyauth` — affected >=0 <1.0.1-0.20260401140714-fc1d4f2082a5

## Details
### Summary

All three OAuth service implementations (`GenericOAuthService`, `GithubOAuthService`, `GoogleOAuthService`) store PKCE verifiers and access tokens as mutable struct fields on singleton instances shared across all concurrent requests. When two users initiate OAuth login for the same provider concurrently, a race condition between `VerifyCode()` and `Userinfo()` causes one user to receive a session with the other user's identity.

### Details

The [`OAuthBrokerService.GetService()`](https://github.com/steveiliop56/tinyauth/blob/592b7ded24959013f8af63ab9930254c752c8c8e/internal/service/oauth_broker_service.go#L70-L72) returns a single shared instance per provider for every request. The OAuth flow stores intermediate state as struct fields on this singleton:

**Token storage** — [`generic_oauth_service.go` line 96](https://github.com/steveiliop56/tinyauth/blob/592b7ded24959013f8af63ab9930254c752c8c8e/internal/service/generic_oauth_service.go#L96):
```go
generic.token = token  // Shared mutable field on singleton
```

**Verifier storage** — [`generic_oauth_service.go` line 81](https://github.com/steveiliop56/tinyauth/blob/592b7ded24959013f8af63ab9930254c752c8c8e/internal/service/generic_oauth_service.go#L81):
```go
generic.verifier = verifier  // Shared mutable field on singleton
```

In the callback handler [`oauth_controller.go` lines 136–143](https://github.com/steveiliop56/tinyauth/blob/592b7ded24959013f8af63ab9930254c752c8c8e/internal/controller/oauth_controller.go#L136-L143), the code calls:
```go
err = service.VerifyCode(code)                       // line 136 — stores token on singleton
// ... race window ...
user, err := controller.broker.GetUser(req.Provider)  // line 143 — reads token from singleton
```

Between these two calls, a concurrent request's `VerifyCode()` can overwrite the `token` field, causing `GetUser()` → `Userinfo()` to fetch the **wrong user's** identity claims.

The same pattern exists in all three implementations:
- [`github_oauth_service.go` lines 34–39, 77, 86–99](https://github.com/steveiliop56/tinyauth/blob/592b7ded24959013f8af63ab9930254c752c8c8e/internal/service/github_oauth_service.go#L34-L39)
- [`google_oauth_service.go` lines 22–27, 65, 73–87](https://github.com/steveiliop56/tinyauth/blob/592b7ded24959013f8af63ab9930254c752c8c8e/internal/service/google_oauth_service.go#L22-L27)

### PoC

**Race scenario** (two concurrent OAuth callbacks):

1. User A and User B both click "Login with GitHub" on the same tinyauth instance
2. Both are redirected to GitHub, authorize, and GitHub redirects both back with authorization codes
3. Both callbacks arrive at tinyauth nearly simultaneously:

```
Timeline:
  t0: Request A → service.VerifyCode(codeA) → singleton.token = tokenA
  t1: Request B → service.VerifyCode(codeB) → singleton.token = tokenB  (overwrites tokenA)
  t2: Request A → broker.GetUser("github")  → Userinfo() reads singleton.token = tokenB
  t3: Request A receives User B's identity (email, name, groups)
```

User A now has a tinyauth session with User B's email, gaining access to all resources User B is authorized for via tinyauth's ACL.

**PKCE verifier DoS variant**: Even with PKCE, concurrent `oauthURLHandler` calls overwrite the `verifier` field, causing `VerifyCode()` to send the wrong verifier to the OAuth provider, which rejects the exchange.

**Static verification**: Run Go's race detector on a test that calls `VerifyCode` and `Userinfo` concurrently on the same service instance — the `-race` flag will flag data races on the `token` and `verifier` fields.

**Go race detector confirmation**: Running a concurrent test with `go test -race` on the singleton service detects **4 data races** on the `token` and `verifier` fields. Without the race detector, measured token overwrite rate is 99.9% (9,985/10,000 iterations).

**Test environment**: tinyauth v5.0.4, commit `592b7ded`, Go race detector + source code analysis

### Impact

An attacker who times their OAuth callback to race with a victim's callback can obtain a tinyauth session with the victim's identity. This grants unauthorized access to all resources the victim is permitted to access through tinyauth's ACL system. The probability of collision increases with concurrent OAuth traffic.

The PKCE verifier overwrite additionally causes a denial-of-service: concurrent OAuth logins for the same provider reliably fail.

### Suggested Fix

Pass verifier and token through method parameters or return values instead of storing them on the singleton:

```go
func (generic *GenericOAuthService) VerifyCode(code string, verifier string) (*oauth2.Token, error) {
    return generic.config.Exchange(generic.context, code, oauth2.VerifierOption(verifier))
}

func (generic *GenericOAuthService) Userinfo(token *oauth2.Token) (config.Claims, error) {
    client := generic.config.Client(generic.context, token)
    // ...
}
```

Store the PKCE verifier in the session/cookie associated with the OAuth `state` parameter, not on the service struct.

## References
- https://github.com/steveiliop56/tinyauth/security/advisories/GHSA-9q5m-jfc4-wc92
- https://nvd.nist.gov/vuln/detail/CVE-2026-33544
- https://github.com/steveiliop56/tinyauth/commit/f26c2171610d5c2dfbba2edb6ccd39490e349803
- https://github.com/steveiliop56/tinyauth
- https://github.com/steveiliop56/tinyauth/releases/tag/v5.0.5
