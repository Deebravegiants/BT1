# [H] SuiteCRM has Authenticated SQL Injection in Authentication Module

## Summary
Severity: High
Advisory: CVE-2026-33288
Aliases: GHSA-7g39-m4fg-vrq7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-33288
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, a SQL Injection vulnerability exists in the SuiteCRM authentication mechanisms when directory support is enabled. The application fails to properly sanitize the user-supplied username before using it in a local database query. An attacker with valid, low-privilege directory credentials can exploit this to execute arbitrary SQL commands, leading to complete privilege escalation (e.g., logging in as the CRM Administrator). Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33288.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-7g39-m4fg-vrq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33288
