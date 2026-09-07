# [M] Cross-Site Request Forgery in Jenkins Jianliao Notification Plugin

## Summary
Severity: Medium
Advisory: GHSA-q8v3-7h6q-g39q
CVE: CVE-2022-34205
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-q8v3-7h6q-g39q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jianliao` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Jianliao Notification Plugin 1.1 and earlier allows attackers to send HTTP POST requests to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34205
- https://github.com/jenkinsci/jianliao-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2240
