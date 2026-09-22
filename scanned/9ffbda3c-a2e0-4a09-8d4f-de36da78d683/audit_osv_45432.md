# [M] nghttp2's nghttpx proxy through 1.69.0 forwards an HTTP/1.1 Upgrade request that also carries a...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1157
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1157
Type: osv

## Affected
- Julia: `nghttp2_jll` — affected >=0 <1.70.0+0

## Details
nghttp2's nghttpx proxy through 1.69.0 forwards an HTTP/1.1 Upgrade request that also carries a Content-Length header and body onto reusable keep-alive backend connections, re-adding the Upgrade and Connection headers while passing Content-Length verbatim. A backend that resolves the resulting ambiguous message in the attacker's favor enables HTTP request/response smuggling and cross-client response-queue poisoning.

## References
- https://github.com/advisories/GHSA-xrr7-82jr-v58x
- https://github.com/bikini/exploitarium/tree/main/nghttp2-nghttpx-upgrade-queue-poison-poc
- https://github.com/nghttp2/nghttp2/commit/ab28105c4a0197da24f8bfc414bc116055249e1e
- https://nvd.nist.gov/vuln/detail/CVE-2026-58055
- https://www.vulncheck.com/advisories/nghttp2-nghttpx-http-request-response-smuggling-via-upgrade-request-with-content-length
