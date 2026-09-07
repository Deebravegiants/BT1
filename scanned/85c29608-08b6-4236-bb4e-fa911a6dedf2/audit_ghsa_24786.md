# [H] Missing permission checks in Jenkins Periodic Backup Plugin allow every user to change settings

## Summary
Severity: High
Advisory: GHSA-5293-3fgp-cr3x
CVE: CVE-2017-1000086
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5293-3fgp-cr3x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:periodicbackup` — affected >=0 <1.5

## Details
The Periodic Backup Plugin did not perform any permission checks, allowing any user with Overall/Read access to change its settings, trigger backups, restore backups, download backups, and also delete all previous backups via log rotation. Additionally, the plugin was not requiring requests to its API be sent via POST, thereby opening itself to Cross-Site Request Forgery attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000086
- https://jenkins.io/security/advisory/2017-07-10
- http://www.securityfocus.com/bid/100437
