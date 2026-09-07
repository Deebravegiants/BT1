# [H] Cross-site request forgery vulnerability in Jenkins WebSphere Deployer Plugin

## Summary
Severity: High
Advisory: GHSA-c3wf-rrhq-rfp2
CVE: CVE-2019-16560
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c3wf-rrhq-rfp2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:websphere-deployer` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins WebSphere Deployer Plugin 1.6.1 and earlier allows attackers to perform connection tests and determine whether files with an attacker-specified path exist on the Jenkins master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16560
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1371
- http://www.openwall.com/lists/oss-security/2019/12/17/1
