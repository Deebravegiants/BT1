# [C] SQL injection with _actor parameter in GLPI

## Summary
Severity: Critical
Advisory: CVE-2022-31056
Aliases: GHSA-9q9x-7xxh-w4cg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2022-31056
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, Data center management, ITIL Service Desk, licenses tracking and software auditing. In affected versions all assistance forms (Ticket/Change/Problem) permit sql injection on the actor fields. This issue has been resolved in version 10.0.2 and all affected users are advised to upgrade.

## References
- http://packetstormsecurity.com/files/171656/GLPI-10.0.2-SQL-Injection-Remote-Code-Execution.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31056.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-9q9x-7xxh-w4cg
- https://nvd.nist.gov/vuln/detail/CVE-2022-31056
