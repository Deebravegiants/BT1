# [M] Grav < 2.0.4 SSRF via Unrestricted cURL Protocols

## Summary
Severity: Medium
Advisory: CVE-2026-62234
Aliases: CVE-2026-62668, GHSA-58q8-f7v4-w2vf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62234
Type: osv

## Details
Grav before 2.0.4 fails to restrict cURL protocols in webhook dispatch, allowing authenticated users with api.webhooks.write permission to create webhooks with file://, dict://, or gopher:// URLs. Attackers can trigger webhook events to read local files, access process information, or pivot to internal services via unrestricted protocol handlers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62234.json
- https://github.com/getgrav/grav/security/advisories/GHSA-58q8-f7v4-w2vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-62234
- https://www.vulncheck.com/advisories/grav-ssrf-via-unrestricted-curl-protocols
- https://github.com/getgrav/grav
