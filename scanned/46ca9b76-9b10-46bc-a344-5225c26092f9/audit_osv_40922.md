# [M] Cap-go - SQL Injection in Cloudflare Analytics Engine Queries via cloudflare.ts

## Summary
Severity: Medium
Advisory: CVE-2026-56221
Aliases: GHSA-f83x-p28r-pf74
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56221
Type: osv

## Details
Cap-go before 12.128.2 contains multiple SQL injection vulnerabilities in cloudflare.ts where user-controlled values from API request bodies are interpolated directly into SQL query strings without sanitization or parameterization. Authenticated users with read-level API key permissions can inject arbitrary SQL through deviceIds, search, version_name, cursor, and actions parameters to access analytics data belonging to other users or applications.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56221.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-f83x-p28r-pf74
- https://nvd.nist.gov/vuln/detail/CVE-2026-56221
- https://www.vulncheck.com/advisories/cap-go-sql-injection-in-cloudflare-analytics-engine-queries-via-cloudflare-ts
