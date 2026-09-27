# [M] siyuan before v3.8.2 SQL Injection via fullTextSearchBlock

## Summary
Severity: Medium
Advisory: CVE-2026-87807
Aliases: GHSA-336w-67gx-gx2h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87807
Type: osv

## Details
siyuan versions before v3.8.2 contain an authenticated SQL injection vulnerability in the fullTextSearchBlock endpoint's method=1 query parameter. Attackers can inject UNION SELECT statements to read the entire blocks table, bypassing publish-access controls and exposing all document content and sensitive attributes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87807.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-336w-67gx-gx2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-87807
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-sql-injection-via-fulltextsearchblock
