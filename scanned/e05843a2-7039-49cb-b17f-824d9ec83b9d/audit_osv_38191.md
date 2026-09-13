# [C] EcclesiaCRM has a Critical SQL Injection

## Summary
Severity: Critical
Advisory: CVE-2026-35184
Aliases: GHSA-gjw3-73q9-v2qh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35184
Type: osv

## Details
EcclesiaCRM is CRM Software for church management. Prior to 8.0.0, there is a SQL injection vulnerability in v2/templates/query/queryview.php via the custom and value parameters. This vulnerability is fixed in 8.0.0.

## References
- https://gist.github.com/NicolasPauferro/d877992327592f1e8eb4e2c9dce1ae9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35184.json
- https://github.com/phili67/ecclesiacrm/security/advisories/GHSA-gjw3-73q9-v2qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-35184
- https://github.com/phili67/ecclesiacrm/commit/f743b97f89da469a4c70b82bd61d0a59a3a957a9
- https://github.com/phili67/ecclesiacrm/pull/2861
