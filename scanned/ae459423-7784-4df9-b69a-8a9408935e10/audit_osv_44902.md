# [M] Traefik: Rootless HTTP/1 request-target routes as "/" but is forwarded verbatim, bypassing path-scoped routing, middleware guards and access logging

## Summary
Severity: Medium
Advisory: CVE-2026-88009
Aliases: GHSA-f52w-8j3h-j724
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88009
Type: osv

## Details
Traefik is an open source HTTP reverse proxy and load balancer. Prior to 2.11.57, and 3.7.13, Traefik accepts a rootless HTTP/1 request target that Go stores in URL.Opaque while leaving URL.Path empty. The rewriteRequestBuilder path evaluates routing, path sanitization, forwardAuth, encodedCharacters, and access logging against a path normalized to / but forwards URL.Opaque verbatim to the backend, allowing cross-vhost routing bypass, path-scoped authorization bypass, and access-log evasion when the backend interprets the opaque target as a path. This issue is fixed in 2.11.57 and 3.7.13.

## References
- https://github.com/traefik/traefik/releases/tag/v2.11.57
- https://github.com/traefik/traefik/releases/tag/v3.7.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88009.json
- https://github.com/traefik/traefik/security/advisories/GHSA-f52w-8j3h-j724
- https://nvd.nist.gov/vuln/detail/CVE-2026-88009
- https://github.com/traefik/traefik/commit/58d1e9ca204526823211e30fd4634101c59d58e9
- https://github.com/traefik/traefik/pull/13796
