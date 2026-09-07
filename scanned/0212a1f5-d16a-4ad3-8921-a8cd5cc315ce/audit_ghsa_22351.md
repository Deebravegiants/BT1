# [M] Incorrect Authorization in Jenkins Git Plugin

## Summary
Severity: Medium
Advisory: GHSA-46p2-fwqg-3h6m
CVE: CVE-2018-1000110
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-46p2-fwqg-3h6m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <3.8.0

## Details
An improper authorization vulnerability exists in Jenkins Git Plugin version 3.7.0 and earlier in GitStatus.java that allows an attacker with network access to obtain a list of nodes and users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000110
- https://github.com/jenkinsci/git-plugin/commit/a3d3a7eb7f75bfe97a0291e3b6d074aafafa86c9
- https://github.com/jenkinsci/git-plugin
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-723
