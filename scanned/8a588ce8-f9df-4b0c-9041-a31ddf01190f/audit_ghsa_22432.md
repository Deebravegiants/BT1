# [M] CSRF vulnerability in Jenkins Database Plugin

## Summary
Severity: Medium
Advisory: GHSA-9rvw-7mx7-h53x
CVE: CVE-2020-2241
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9rvw-7mx7-h53x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:database` — affected >=0 <1.7

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins database Plugin 1.6 and earlier allows attackers to connect to an attacker-specified database server using attacker-specified credentials.

Database Plugin 1.7 requires POST requests for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2241
- https://github.com/jenkinsci/database-plugin/commit/7a438d96897af0034cb2e06db0819ca4595c24cb
- https://github.com/jenkinsci/database-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1024
- http://www.openwall.com/lists/oss-security/2020/09/01/3
