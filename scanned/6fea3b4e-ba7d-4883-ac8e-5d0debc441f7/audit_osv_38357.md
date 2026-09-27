# [H] ChurchCRM has a Blind SQL injection in PropertyAssign.php

## Summary
Severity: High
Advisory: CVE-2026-39330
Aliases: GHSA-xq86-jh52-728g
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39330
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, an SQL injection vulnerability was found in the endpoint /PropertyAssign.php in ChurchCRM. Authenticated users with the role Manage Groups & Roles (ManageGroups) and Edit Records (isEditRecordsEnabled) can inject arbitrary SQL statements through the Value parameter and thus extract and modify information from the database. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39330.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-xq86-jh52-728g
- https://nvd.nist.gov/vuln/detail/CVE-2026-39330
