# [M] Traefik: respondingTimeouts.readTimeout is not applied to HTTP/3, leaving slow-body uploads unbounded

## Summary
Severity: Medium
Advisory: CVE-2026-88012
Aliases: CVE-2026-88878, GHSA-7ghq-v6jf-g56c
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88012
Type: osv

## Details
Traefik is an open source HTTP reverse proxy and load balancer. From 2.8.2 until 2.11.56 and 3.7.12, HTTP/3 entrypoints do not apply entryPoints..transport.respondingTimeouts.readTimeout because the timeout is enforced on a TCP connection and the HTTP/3 server has no corresponding QUIC stream deadline. An unauthenticated client can use a slow request body, trickling data indefinitely while holding a request and an upstream connection open and exhausting backends with bounded connection pools. This issue is fixed in 2.11.56 and 3.7.12.

## References
- https://github.com/traefik/traefik/releases/tag/v2.11.56
- https://github.com/traefik/traefik/releases/tag/v3.7.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88012.json
- https://github.com/traefik/traefik/security/advisories/GHSA-7ghq-v6jf-g56c
- https://nvd.nist.gov/vuln/detail/CVE-2026-88012
- https://github.com/traefik/traefik/commit/a8d0bc425859dde7481a6c9a324e610b81d754d0
- https://github.com/traefik/traefik/pull/13717
