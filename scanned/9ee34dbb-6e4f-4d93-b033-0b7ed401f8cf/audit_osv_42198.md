# [M] Verba (goldenverba) Server-Side Request Forgery via /api/connect and Same-Origin Middleware Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-65317
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-65317
Type: osv

## Details
Verba RAG application version 2.1.3 contains a server-side request forgery vulnerability combined with a same-origin middleware bypass that allows unauthenticated remote attackers to make the server issue arbitrary HTTP requests by supplying a crafted Origin header and attacker-controlled host and port values. Attackers can bypass the localhost origin check in the API middleware by sending any Origin value prefixed with ' regardless of port, then submit arbitrary host and port parameters to the /api/connect endpoint to cause the server to issue outbound GET requests to attacker-controlled infrastructure.

## References
- https://github.com/geo-chen/oss/blob/main/verba.md#finding-2-ssrf--same-origin-middleware-bypass-in-apiconnect----goldenverba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65317.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65317
- https://www.vulncheck.com/advisories/verba-goldenverba-server-side-request-forgery-via-api-connect-and-same-origin-middleware-bypass
- https://github.com/weaviate/Verba
