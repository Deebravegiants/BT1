# [C] Incomplete fix for CVE-2026-35184: SQL Injection in phili67/ecclesiacrm

## Summary
Severity: Critical
Advisory: CVE-2026-44418
Aliases: GHSA-vmgq-gpf9-mjjj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44418
Type: osv

## Details
EcclesiaCRM is CRM Software for church management. In 8.0.0 and earlier, the ValidateInput() function's default case in EcclesiaCRM's query view passes user-supplied POST parameters directly into SQL queries via str_replace without any sanitization, enabling SQL injection through query parameters that use non-standard validation types. This is caused by an incomplete fix for CVE-2026-35184.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44418.json
- https://github.com/phili67/ecclesiacrm/security/advisories/GHSA-vmgq-gpf9-mjjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44418
- https://github.com/phili67/ecclesiacrm/commit/f743b97f89da469a4c70b82bd61d0a59a3a957a9
