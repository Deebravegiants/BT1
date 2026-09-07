# [M] XSS vulnerability in Jenkins Subversion Partial Release Manager Plugin

## Summary
Severity: Medium
Advisory: GHSA-qmf3-w5jf-cv54
CVE: CVE-2020-2199
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qmf3-w5jf-cv54
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:svn-partial-release-mgr` — affected >=0

## Details
Subversion Partial Release Manager Plugin 1.0.1 and earlier does not escape the error message for the repository URL field form validation.

This results in a reflected cross-site scripting (XSS) vulnerability that can also be exploited similar to a stored cross-site scripting vulnerability by users with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2199
- https://github.com/jenkinsci/svn-partial-release-mgr-plugin
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1726
- http://www.openwall.com/lists/oss-security/2020/06/03/3
