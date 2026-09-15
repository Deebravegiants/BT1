# [H] ChurchCRM has SQL Injection in eGive Import Feature

## Summary
Severity: High
Advisory: CVE-2025-68111
Aliases: GHSA-c4vm-87vf-hmx9
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68111
Type: osv

## Details
ChurchCRM is an open-source church management system. In versions prior to 6.5.3, a SQL injection vulnerability exists in the `eGive.php` file within the "ReImport" functionality. An authenticated user with finance privileges can execute arbitrary SQL queries by manipulating the `MissingEgive_FamID_...` POST parameter. This can lead to unauthorized data access, modification, or deletion within the database. Version 6.5.3 has a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68111.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-c4vm-87vf-hmx9
- https://nvd.nist.gov/vuln/detail/CVE-2025-68111
