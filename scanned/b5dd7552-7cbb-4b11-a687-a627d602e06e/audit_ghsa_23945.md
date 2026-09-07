# [M] Improper Authentication in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-q4cq-r7hg-pxqq
CVE: CVE-2018-1999045
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q4cq-r7hg-pxqq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.121.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.122 <2.138

## Details
A improper authentication vulnerability exists in Jenkins 2.137 and earlier, 2.121.2 and earlier in SecurityRealm.java, TokenBasedRememberMeServices2.java that allows attackers with a valid cookie to remain logged in even if that feature is disabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999045
- https://github.com/jenkinsci/jenkins/commit/24d350d8a6f033bf32c94b3f7cca2d1ab2f9df03
- https://github.com/jenkinsci/jenkins/commit/ef9583a24abc4de157e1570cb32d7a273d327f36
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-08-15/#SECURITY-996
