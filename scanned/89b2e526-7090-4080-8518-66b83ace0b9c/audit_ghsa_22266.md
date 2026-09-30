# [M] Missing permission check in Jenkins Support Core Plugin

## Summary
Severity: Medium
Advisory: GHSA-j52r-pmqv-wm38
CVE: CVE-2019-16539
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j52r-pmqv-wm38
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:support-core` — affected >=0 <2.64

## Details
A missing permission check in Jenkins Support Core Plugin 2.63 and earlier allows attackers with Overall/Read permission to delete support bundles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16539
- https://github.com/jenkinsci/support-core-plugin/commit/6b177ea7cc7347e13fa87174472400bbbe78d422
- https://github.com/jenkinsci/support-core-plugin
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1634
- http://www.openwall.com/lists/oss-security/2019/11/21/1
