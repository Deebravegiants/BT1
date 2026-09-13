# [H] ChurchCRM has a SQL Injection in PropertyTypeEditor.php via Incorrect Sanitizer Substitution

## Summary
Severity: High
Advisory: CVE-2026-39340
Aliases: GHSA-66f7-4p96-mww9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39340
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, a SQL injection vulnerability exists in PropertyTypeEditor.php, part of the administration functionality for managing property type categories (People → Person Properties / Family Properties). The vulnerability was introduced when legacyFilterInput() which both strips HTML and escapes SQL — was replaced with sanitizeText(), which strips HTML only. User-supplied values from the Name and Description fields are concatenated directly into raw INSERT and UPDATE queries with no SQL escaping. This allows any authenticated user with the MenuOptions role (a non-admin staff permission) to perform time-based blind injection and exfiltrate any data from the database, including password hashes of all users. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39340.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-66f7-4p96-mww9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39340
