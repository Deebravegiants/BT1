# [M] Budibase before 3.38.1 SSRF Blacklist Bypass via HTTP Redirect

## Summary
Severity: Medium
Advisory: CVE-2026-67311
Aliases: GHSA-86f3-cqpq-wp9m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67311
Type: osv

## Details
Budibase before 3.38.1 contains a server-side request forgery vulnerability in the REST datasource integration that fails to validate HTTP redirects against the IP blacklist. Attackers with Builder role can configure a REST datasource pointing to an external server that returns a redirect to internal IP addresses, bypassing blacklist protection to access cloud metadata endpoints and internal services.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-86f3-cqpq-wp9m
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67311.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67311
- https://www.vulncheck.com/advisories/budibase-before-ssrf-blacklist-bypass-via-http-redirect
