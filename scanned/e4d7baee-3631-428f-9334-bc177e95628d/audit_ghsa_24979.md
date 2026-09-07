# [M] Injection in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-7592-93rm-6gpx
CVE: CVE-2018-1000193
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7592-93rm-6gpx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.107.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.108 <2.121

## Details
A improper neutralization of control sequences vulnerability exists in Jenkins 2.120 and older, LTS 2.107.2 and older in HudsonPrivateSecurityRealm.java that allows users to sign up using user names containing control characters that can then appear to have the same name as other users, and cannot be deleted via the UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000193
- https://github.com/jenkinsci/jenkins/commit/de7aaab441151fb1760855fec83681c6a8756a45
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-786
- https://www.oracle.com/security-alerts/cpuapr2022.html
