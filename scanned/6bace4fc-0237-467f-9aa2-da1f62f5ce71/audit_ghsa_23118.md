# [M] Incorrect Authorization in Jenkins Mercurial Plugin

## Summary
Severity: Medium
Advisory: GHSA-f9cx-789c-w2mr
CVE: CVE-2018-1000112
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-f9cx-789c-w2mr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=0 <2.3

## Details
An improper authorization vulnerability exists in Jenkins Mercurial Plugin version 2.2 and earlier in MercurialStatus.java that allows an attacker with network access to obtain a list of nodes and users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000112
- https://github.com/jenkinsci/mercurial-plugin/commit/54b4f82e80c89d51b12bc64258f6b59e98b0c16a
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-726
