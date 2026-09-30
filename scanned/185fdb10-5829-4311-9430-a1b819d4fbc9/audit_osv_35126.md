# [C] ChurchCRM vulnerable to time-based blind SQL Injection in ConfirmReportEmail.php

## Summary
Severity: Critical
Advisory: CVE-2025-68400
Aliases: GHSA-v54g-2pvg-gvp2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68400
Type: osv

## Details
ChurchCRM is an open-source church management system. A SQL Injection vulnerability exists in the legacy endpoint `/Reports/ConfirmReportEmail.php` in ChurchCRM prior to version 6.5.3. Although the feature was removed from the UI, the file remains deployed and reachable directly via URL. This is a classic case of *dead but reachable code*. Any authenticated user - including one with zero assigned permissions - can exploit SQL injection through the `familyId` parameter. Version 6.5.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68400.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-v54g-2pvg-gvp2
- https://nvd.nist.gov/vuln/detail/CVE-2025-68400
