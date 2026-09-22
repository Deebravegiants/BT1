# [H] NoSQL Injection Risk via Unsanitized Query Parameters

## Summary
Severity: High
Advisory: CVE-2026-25814
Aliases: GHSA-gmg6-mv7g-xjfv
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25814
Type: osv

## Details
PlaciPy is a placement management system designed for educational institutions. In version 1.0.0, User-controlled query parameters are passed directly into DynamoDB query/filter construction without validation or sanitization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25814.json
- https://github.com/Praskla-Technology/assessment-placipy/security/advisories/GHSA-gmg6-mv7g-xjfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-25814
