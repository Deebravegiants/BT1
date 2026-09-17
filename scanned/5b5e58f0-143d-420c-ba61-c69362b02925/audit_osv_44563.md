# [H] HTTPX2: Secure WebSocket traffic sent without TLS through SOCKS proxies

## Summary
Severity: High
Advisory: CVE-2026-84381
Aliases: GHSA-7mj9-2mp8-4m2p, PYSEC-2026-3844, PYSEC-2026-3845
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84381
Type: osv

## Details
HTTPX2 is a next generation HTTP client for Python. Prior to 2.10.0, httpcore2 fails to start TLS in src/httpcore2/httpcore2/_sync/socks_proxy.py and src/httpcore2/httpcore2/_async/socks_proxy.py when the remote origin uses wss through a SOCKS5 proxy because the TLS upgrade condition only recognizes https. HTTPX2 exposes the flaw through Client.websocket() and AsyncClient.websocket() from 2.6.0 through 2.9.1, so the opening handshake, query parameters, Authorization headers, cookies, and subsequent frames can cross the proxy path in plaintext without certificate verification. An attacker controlling or observing that path can read or modify traffic and impersonate the WebSocket server. This issue is fixed in httpcore2 2.10.0 and HTTPX2 2.10.0.

## References
- https://github.com/pydantic/httpx2/releases/tag/v2.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84381.json
- https://github.com/pydantic/httpx2/security/advisories/GHSA-7mj9-2mp8-4m2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-84381
- https://github.com/pydantic/httpx2/commit/fb008dd700b761d955210d9692475c3e2f379453
- https://github.com/pydantic/httpx2/pull/1104
