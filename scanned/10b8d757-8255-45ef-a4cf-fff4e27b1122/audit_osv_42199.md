# [M] Verba (goldenverba) Unauthenticated Server-Side Request Forgery via WebSocket Import Endpoint HTMLReader

## Summary
Severity: Medium
Advisory: CVE-2026-65318
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-65318
Type: osv

## Details
Verba RAG application version 2.1.3 contains an unauthenticated server-side request forgery vulnerability that allows unauthenticated attackers to cause the backend to issue arbitrary HTTP GET requests by supplying attacker-controlled URLs through the WebSocket import endpoint. Attackers can connect to the /ws/import_files WebSocket endpoint without authentication, specify arbitrary URLs in the HTMLReader configuration, and cause the server to fetch internal resources such as co-located database endpoints or cloud instance metadata services to retrieve sensitive credentials.

## References
- https://github.com/geo-chen/oss/blob/main/verba.md#finding-1-unauthenticated-ssrf-in-verba-websocket-import-endpoint-htmlreader
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65318.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65318
- https://www.vulncheck.com/advisories/verba-goldenverba-unauthenticated-server-side-request-forgery-via-websocket-import-endpoint-htmlreader
- https://github.com/weaviate/Verba
