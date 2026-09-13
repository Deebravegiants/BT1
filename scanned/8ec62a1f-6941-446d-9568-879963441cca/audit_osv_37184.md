# [H] SuiteCRM vulnerable to Authenticated SQL Injection via unsanitized field_function in Report Fields

## Summary
Severity: High
Advisory: CVE-2026-29096
Aliases: GHSA-vh42-gmqm-q55m
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29096
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, when creating or editing a report (AOR_Reports module), the `field_function` parameter from POST data is saved directly into the `aor_fields` table without any validation. Later, when the report is executed/viewed, this value is concatenated directly into a SQL SELECT query without sanitization, enabling second-order SQL injection. Any authenticated user with Reports access can extract arbitrary database contents (password hashes, API tokens, config values). On MySQL with FILE privilege, this could lead to RCE via SELECT INTO OUTFILE. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29096.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-vh42-gmqm-q55m
- https://nvd.nist.gov/vuln/detail/CVE-2026-29096
