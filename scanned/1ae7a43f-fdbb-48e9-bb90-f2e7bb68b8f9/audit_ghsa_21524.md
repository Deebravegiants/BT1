# [M] Cross-Site Request Forgery in Jenkins Delete log Plugin

## Summary
Severity: Medium
Advisory: GHSA-hw4f-g7wh-xp52
CVE: CVE-2022-45393
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-hw4f-g7wh-xp52
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:delete-log-plugin` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Delete log Plugin 1.0 and earlier allows attackers to delete build logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45393
- https://github.com/jenkinsci/delete-log-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2920
- http://www.openwall.com/lists/oss-security/2022/11/15/4
