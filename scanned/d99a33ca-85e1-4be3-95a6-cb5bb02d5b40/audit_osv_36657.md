# [H] Church CRM has SQL injection in PaddleNumEditor.php

## Summary
Severity: High
Advisory: CVE-2026-24854
Aliases: GHSA-p3q7-q68q-h2gr
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-30
Source: https://osv.dev/vulnerability/CVE-2026-24854
Type: osv

## Details
ChurchCRM is an open-source church management system. A SQL Injection vulnerability exists in endpoint `/PaddleNumEditor.php` in ChurchCRM prior to version 6.7.2. Any authenticated user, including one with zero assigned permissions, can exploit SQL injection through the `PerID` parameter. Version 6.7.2 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24854.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-p3q7-q68q-h2gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24854
- http://github.com/ChurchCRM/CRM/commit/748f5084fc06c5e12463dc7fdd62d1d31fc08d38
