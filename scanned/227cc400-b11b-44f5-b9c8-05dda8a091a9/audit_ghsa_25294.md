# [M] CSRF vulnerability in Jenkins ElasTest Plugin

## Summary
Severity: Medium
Advisory: GHSA-66rm-wg7m-8pgv
CVE: CVE-2020-2273
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-66rm-wg7m-8pgv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:elastest` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins ElasTest Plugin 1.2.1 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2273
- https://github.com/jenkinsci/elastest-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1903
- http://www.openwall.com/lists/oss-security/2020/09/16/3
