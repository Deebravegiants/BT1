# [H] ChurchCRM has a Second Order SQLI via FundRaiserEditor.php

## Summary
Severity: High
Advisory: CVE-2026-39319
Aliases: GHSA-vg4m-hc29-jgqj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39319
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 7.1.0, a second order SQL injection vulnerability was found in the endpoint /FundRaiserEditor.php in ChurchCRM. A user has to be authenticated but doesn't need any privileges. These users can inject arbitrary SQL statements through the iCurrentFundraiser PHP session parameter and thus extract and modify information from the database. This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39319.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-vg4m-hc29-jgqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-39319
