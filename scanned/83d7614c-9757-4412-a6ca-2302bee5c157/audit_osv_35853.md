# [H] @fastify/http-proxy vulnerable to prefix escape via WebSocket path traversal

## Summary
Severity: High
Advisory: CVE-2026-15631
Aliases: GHSA-7hrw-592w-9wh2
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-18
Source: https://osv.dev/vulnerability/CVE-2026-15631
Type: osv

## Details
Impact: @fastify/http-proxy versions from 9.4.0 up to and including 11.5.0 fail to validate the resolved WebSocket destination path against the configured rewrite prefix. The WebSocket routing path in WebSocketProxy.findUpstream resolves the destination via the WHATWG URL constructor, which collapses dot segments, so a crafted upgrade request with path traversal sequences can escape the rewrite prefix and reach upstream endpoints that were not meant to be exposed by the proxy. This is a variant of CVE-2021-21322 in a code path that never went through the HTTP fix in fastify/reply-from. Exploitation requires a non-normalizing WebSocket client, since browsers and the ws package normalize the request path before sending, but raw HTTP clients or downstream proxies that forward the request target unchanged make the attack reachable in production topologies. 

Patches: upgrade to @fastify/http-proxy 11.6.0. 

Workarounds: none.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15631.json
- https://github.com/fastify/fastify-http-proxy/security/advisories/GHSA-7hrw-592w-9wh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-15631
