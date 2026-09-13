# [M] Flextype CMS through 1.0.0-alpha.3 API Token Exposure via Query String

## Summary
Severity: Medium
Advisory: CVE-2026-88897
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88897
Type: osv

## Details
Flextype CMS through 1.0.0-alpha.3 accepts API authentication credentials through URL query string parameters in REST API routes. Attackers with access to web server, proxy, or monitoring logs can recover valid API token pairs that grant full API access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88897.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-88897
- https://www.vulncheck.com/advisories/flextype-cms-through-1.0.0-alpha.3-api-token-exposure-via-query-string
- https://github.com/flextype/flextype/issues/598
- https://github.com/flextype/flextype
- https://github.com/flextype/flextype/blob/v1.0.0-alpha.3/src/flextype/core/Endpoints/Api.php
