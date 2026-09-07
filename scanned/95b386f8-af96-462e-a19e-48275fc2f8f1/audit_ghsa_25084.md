# [H] Jenkins Alauda DevOps Pipeline Plugin vulnerable to cross-site request forgery

## Summary
Severity: High
Advisory: GHSA-pv4c-rj4h-gr9m
CVE: CVE-2019-16573
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pv4c-rj4h-gr9m
Type: github-advisory

## Affected
- Maven: `com.alauda.jenkins.plugins:alauda-devops-pipeline` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins Alauda DevOps Pipeline Plugin 2.3.2 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16573
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1600
- http://www.openwall.com/lists/oss-security/2019/12/17/1
