# [H] SQL Injection in Event List via `WhichType` Parameter

## Summary
Severity: High
Advisory: CVE-2025-66395
Aliases: GHSA-c9xf-f3gr-xfwv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-66395
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 6.5.3, a SQL injection vulnerability exists in the `src/ListEvents.php` file. When filtering events by type, the `WhichType` POST parameter is not properly sanitized or type-casted before being used in multiple SQL queries. This allows any authenticated user to execute arbitrary SQL commands, including time-based blind SQL injection attacks. Any authenticated user, regardless of their privilege level, can execute arbitrary queries on the database. This could allow them to exfiltrate, modify, or delete any data in the database, including user credentials, financial data, and personal information, leading to a full compromise of the application's data. Version 6.5.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66395.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-c9xf-f3gr-xfwv
- https://nvd.nist.gov/vuln/detail/CVE-2025-66395
