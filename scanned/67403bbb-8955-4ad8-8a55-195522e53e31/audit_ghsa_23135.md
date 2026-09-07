# [M] CSRF vulnerability in Jenkins Mantis Plugin 

## Summary
Severity: Medium
Advisory: GHSA-wwrr-4jp4-58wg
CVE: CVE-2019-16569
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wwrr-4jp4-58wg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mantis` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins Mantis Plugin 0.26 and earlier allows attackers to connect to an attacker-specified web server using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16569
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1603
- http://www.openwall.com/lists/oss-security/2019/12/17/1
