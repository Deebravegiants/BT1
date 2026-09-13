# [H] ChurchCRM has a SQL Injection in Event Type Editor (Admin)

## Summary
Severity: High
Advisory: CVE-2026-39343
Aliases: GHSA-h2hx-p9gp-q7gr
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39343
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, a SQL injection vulnerability exists in the EditEventTypes.php file, which is only accessible to administrators. The EN_tyid POST parameter is not sanitized before being used in a SQL query, allowing an administrator to execute arbitrary SQL commands directly against the database. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39343.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-h2hx-p9gp-q7gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-39343
