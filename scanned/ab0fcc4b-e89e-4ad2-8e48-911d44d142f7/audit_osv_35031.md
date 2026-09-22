# [H] ChurchCRM has SQL Injection in Event Editor via `EN_tyid` Parameter caused by an Incomplete Fix

## Summary
Severity: High
Advisory: CVE-2025-67751
Aliases: GHSA-wxcc-gvfv-56fg
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-67751
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 6.5.0, a SQL injection vulnerability exists in the `EventEditor.php` file. When creating a new event and selecting an event type, the `EN_tyid` POST parameter is not sanitized. This allows an authenticated user with event management permissions (`isAddEvent`) to execute arbitrary SQL queries. Version 6.5.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67751.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-wxcc-gvfv-56fg
- https://nvd.nist.gov/vuln/detail/CVE-2025-67751
- https://github.com/ChurchCRM/CRM/commit/2d6cf7aed9af1b9b47e125d1a2266f8e2a88f3fd
