# [M] Missing permission checks in Jenkins GitHub Pull Request Builder Plugin

## Summary
Severity: Medium
Advisory: GHSA-w4v5-54p8-m4j5
CVE: CVE-2023-24435
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-w4v5-54p8-m4j5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ghprb` — affected >=0

## Details
A missing permission check in Jenkins GitHub Pull Request Builder Plugin 1.42.2 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24435
- https://github.com/jenkinsci/ghprb-plugin
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2789%20(2)
