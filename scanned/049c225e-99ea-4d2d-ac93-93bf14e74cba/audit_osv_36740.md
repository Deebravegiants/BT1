# [C] OpenBullet2 0.3.2 Authentication Bypass via X-Api-Key Header

## Summary
Severity: Critical
Advisory: CVE-2026-25555
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-25555
Type: osv

## Details
OpenBullet2 through version 0.3.2 contains an authentication bypass vulnerability in the API key authentication middleware that allows unauthenticated attackers to gain admin access by supplying an empty X-Api-Key header value. Attackers can exploit the middleware's comparison of the supplied header against an empty AdminApiKey default string to access the admin console and all API endpoints without valid credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25555.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25555
- https://www.vulncheck.com/advisories/openbullet2-authentication-bypass-via-x-api-key-header
- https://github.com/openbullet/openbullet2
- https://hackernoon.com/one-empty-header-to-admin-how-an-auth-bypass-breaks-openbullet2
