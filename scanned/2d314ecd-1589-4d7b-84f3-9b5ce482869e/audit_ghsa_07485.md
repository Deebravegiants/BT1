# [M] GoFiber Vulnerable to Username Enumeration via Timing Oracle in BasicAuth Default Authorizer

## Summary
Severity: Medium
Advisory: GHSA-g5vh-55hw-rxm8
CVE: CVE-2026-44332
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-g5vh-55hw-rxm8
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v3` — affected >=0 <3.3.0

## Details
## Summary

The default `Authorizer` function in GoFiber's BasicAuth middleware uses short-circuit evaluation that skips password hash comparison for non-existent usernames. With bcrypt-hashed passwords (the primary use case), the timing difference between a valid and invalid username is approximately 1,000,000:1 (~100ms vs ~100ns), enabling reliable remote username enumeration.

## Vulnerable Code

**File:** `middleware/basicauth/config.go`, lines 126-138

```go
if cfg.Authorizer == nil {
    verifiers := make(map[string]func(string) bool, len(cfg.Users))
    for u, hpw := range cfg.Users {
        v, err := parseHashedPassword(hpw)
        if err != nil {
            panic(err)
        }
        verifiers[u] = v
    }
    cfg.Authorizer = func(user, pass string, _ fiber.Ctx) bool {
        verify, ok := verifiers[user]
        return ok && verify(pass)   // line 137: short-circuit skips verify() if user unknown
    }
}
```

## Data Flow

1. Attacker sends `Authorization: Basic <base64(candidate:wrongpass)>`
2. BasicAuth middleware decodes credentials and calls `cfg.Authorizer(user, pass, c)`
3. Map lookup `verifiers[user]` returns `ok=false` for non-existent users
4. Go `&&` short-circuit: `false && verify(pass)` returns immediately without calling `verify()`
5. For valid users, `verify(pass)` executes `bcrypt.CompareHashAndPassword()` (line 167: ~100ms at default cost 10)
6. Timing difference: ~100ns (invalid user) vs ~100ms (valid user) = 1,000,000:1 ratio

**Timing comparison by hash type:**

| Hash Type | Valid User | Invalid User | Ratio |
|-----------|-----------|--------------|-------|
| bcrypt ($2) | ~100 ms | ~100 ns | 1,000,000:1 |
| SHA-512 | ~1-5 us | ~100 ns | 10-50:1 |
| SHA-256 | ~1-5 us | ~100 ns | 10-50:1 |

## Impact

- **Username enumeration:** Attacker reliably determines which usernames exist by measuring response latency
- **Targeted brute force:** After enumerating valid usernames, password brute force is focused only on real accounts
- **Account discovery:** In applications where usernames are sensitive (internal tools, admin panels), leaking their existence is itself a security issue

## Notes

- Password hash comparisons themselves are timing-safe: `subtle.ConstantTimeCompare` is used correctly for SHA-256 (line 185), SHA-512 (line 176), and bcrypt uses its own constant-time comparison
- The fix is to always execute a dummy hash comparison for unknown users: `bcrypt.CompareHashAndPassword(dummyHash, []byte(pass))` and discard the result
- This pattern matches CVE-2023-36456 (Authentik timing oracle) and similar findings in other auth libraries

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-g5vh-55hw-rxm8
- https://github.com/gofiber/fiber
