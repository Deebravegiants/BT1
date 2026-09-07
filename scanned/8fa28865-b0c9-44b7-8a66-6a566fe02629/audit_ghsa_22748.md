# [M] Missing permission checks in Jenkins ElasTest Plugin

## Summary
Severity: Medium
Advisory: GHSA-mr43-vf8q-q5f2
CVE: CVE-2020-2272
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mr43-vf8q-q5f2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:elastest` — affected >=0

## Details
A missing permission check in Jenkins ElasTest Plugin 1.2.1 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2272
- https://github.com/jenkinsci/elastest-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1903
- http://www.openwall.com/lists/oss-security/2020/09/16/3
