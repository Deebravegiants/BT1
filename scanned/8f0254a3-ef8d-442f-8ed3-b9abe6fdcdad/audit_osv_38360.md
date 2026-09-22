# [H] ChurchCRM has a Blind SQL injection in SettingsIndividual.php

## Summary
Severity: High
Advisory: CVE-2026-39334
Aliases: GHSA-8g53-72jr-39w6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39334
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, an SQL injection vulnerability was found in the endpoint /SettingsIndividual.php in ChurchCRM 7.0.5. Authenticated users without any specific privileges can inject arbitrary SQL statements through the type array parameter via the index and thus extract and modify information from the database. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39334.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-8g53-72jr-39w6
- https://nvd.nist.gov/vuln/detail/CVE-2026-39334
