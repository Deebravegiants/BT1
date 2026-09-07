# [M] Improper Neutralization of Input During Web Page Generation in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-pgxv-h967-fw2q
CVE: CVE-2018-1999005
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pgxv-h967-fw2q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.121.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.122 <2.132

## Details
A cross-site scripting vulnerability exists in Jenkins 2.132 and earlier, 2.121.1 and earlier in BuildTimelineWidget.java, BuildTimelineWidget/control.jelly that allows attackers with Job/Configure permission to define JavaScript that would be executed in another user's browser when that other user performs some UI actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999005
- https://github.com/jenkinsci/jenkins/commit/8697bdff0342421e22230028d84aaa265719e86c
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-07-18/#SECURITY-944
- https://www.oracle.com/security-alerts/cpuapr2022.html
