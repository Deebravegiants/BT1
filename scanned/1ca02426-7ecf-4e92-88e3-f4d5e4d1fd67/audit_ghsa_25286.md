# [H] Cross Site Request Forgery in Jenkins SSH Plugin

## Summary
Severity: High
Advisory: GHSA-9g33-48jh-jq7v
CVE: CVE-2022-30958
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-9g33-48jh-jq7v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ssh` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins SSH Plugin 2.6.1 and earlier allows attackers to connect to an attacker-specified SSH server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30958
- https://github.com/jenkinsci/ssh-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2093
