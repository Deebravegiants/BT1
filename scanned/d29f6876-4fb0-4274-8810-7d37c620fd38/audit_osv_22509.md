# [C] SQL injection on login page in GLPI

## Summary
Severity: Critical
Advisory: CVE-2022-31061
Aliases: GHSA-w2gc-v2gm-q7wq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2022-31061
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, Data center management, ITIL Service Desk, licenses tracking and software auditing. In affected versions there is a SQL injection vulnerability which is possible on login page. No user credentials are required to exploit this vulnerability. Users are advised to upgrade as soon as possible. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31061.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-w2gc-v2gm-q7wq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31061
- https://github.com/glpi-project/glpi/commit/21ae07d00d0b3230f6235386e98388cfc5bb0514
