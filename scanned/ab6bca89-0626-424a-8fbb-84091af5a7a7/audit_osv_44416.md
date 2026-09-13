# [M] Budibase Server before 3.41.3 SSRF via Query Import

## Summary
Severity: Medium
Advisory: CVE-2026-82246
Aliases: GHSA-48x3-9ph2-p9gj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82246
Type: osv

## Details
Budibase Server before 3.41.3 contains a server-side request forgery vulnerability in the query import endpoint that fails to validate user-supplied URLs before fetching content. Attackers can submit arbitrary URLs to retrieve responses from internal services including cloud metadata endpoints and other restricted network resources.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-48x3-9ph2-p9gj
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82246.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82246
- https://www.vulncheck.com/advisories/budibase-server-before-3.41.3-ssrf-via-query-import
