# [M] Jenkins Git Parameter Plugin vulnerable to Stored cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-hw26-fw67-qxm9
CVE: CVE-2020-2112
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hw26-fw67-qxm9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.tools:git-parameter` — affected >=0 <0.9.12

## Details
Jenkins Git Parameter Plugin 0.9.11 and earlier does not escape the parameter name shown on the UI, resulting in a stored cross-site scripting vulnerability exploitable by users with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2112
- https://github.com/jenkinsci/git-parameter-plugin/commit/6fd933c5b1af4ec5dc27edfe2c74931dbff69012
- https://github.com/jenkinsci/git-parameter-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1709
- http://www.openwall.com/lists/oss-security/2020/02/12/3
