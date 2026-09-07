# [M] Incorrect Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-p265-xr98-3vmr
CVE: CVE-2018-1999003
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p265-xr98-3vmr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.121.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.122 <2.133

## Details
A Improper authorization vulnerability exists in Jenkins 2.132 and earlier, 2.121.1 and earlier in Queue.java that allows attackers with Overall/Read permission to cancel queued builds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999003
- https://github.com/jenkinsci/jenkins/commit/af9e11c9941487f69ec1a95c65958fc208064e7a
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-07-18/#SECURITY-891
- https://www.oracle.com/security-alerts/cpuapr2022.html
