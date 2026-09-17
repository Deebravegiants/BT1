# [H] @fastify/http-proxy vulnerable to prefix escape via backslash dot-segments

## Summary
Severity: High
Advisory: CVE-2026-85124
Aliases: GHSA-qv33-689p-2xq5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85124
Type: osv

## Details
@fastify/http-proxy versions before 11.6.2 do not validate proxied HTTP request paths for backslash based dot-segments before forwarding them to the configured upstream. The plain HTTP request handler skips the destination validation that the WebSocket path performs, and the underlying reply-from library only rejects forward-slash traversal, so a request containing backslash dot-segments can escape the boundary set by the prefix and rewritePrefix options. An unauthenticated network attacker can use this to reach upstream paths that were meant to stay hidden behind the proxy, resulting in disclosure of internal endpoints. This is a path traversal issue (CWE-22). Users should upgrade to @fastify/http-proxy 11.6.2 or later.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85124.json
- https://github.com/fastify/fastify-http-proxy/security/advisories/GHSA-qv33-689p-2xq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-85124
