# [M] ChurchCRM has Authenticated SQL Injection in `/api/families/byCheckNumber/{scanString}`

## Summary
Severity: Medium
Advisory: CVE-2026-40482
Aliases: GHSA-hc37-vx3w-34fg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40482
Type: osv

## Details
ChurchCRM is an open-source church management system. Versions prior to 7.2.0 have SQL injection in FinancialService::getMemberByScanString() via unsanitized $routeAndAccount concatenated into raw SQL. This issue has been fixed in version 7.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40482.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-hc37-vx3w-34fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-40482
- https://github.com/ChurchCRM/CRM/commit/214694eb83778e1f5e52b3dfa2a99d0e965c1850
- https://github.com/ChurchCRM/CRM/pull/8607
