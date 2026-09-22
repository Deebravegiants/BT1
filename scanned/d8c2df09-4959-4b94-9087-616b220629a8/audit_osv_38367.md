# [C] ChurchCRM has a SQL injection searchwhat parameter via QueryView.php

## Summary
Severity: Critical
Advisory: CVE-2026-39342
Aliases: GHSA-7fr4-mvfm-cxfx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39342
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, the searchwhat parameter via QueryView.php with the QueryID=15 is vulnerable to a SQL injection. The authenticated user requires access to Data/Reports > Query Menu and access to the "Advanced Search" query. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39342.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-7fr4-mvfm-cxfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-39342
