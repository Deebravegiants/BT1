# [M] Jenkins allows attackers to determine whether a user exists

## Summary
Severity: Medium
Advisory: GHSA-9vg9-x38g-9hfx
CVE: CVE-2014-2064
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9vg9-x38g-9hfx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.533 <1.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.532.2

## Details
The loadUserByUsername function in hudson/security/HudsonPrivateSecurityRealm.java in Jenkins before 1.551 and LTS before 1.532.2 allows remote attackers to determine whether a user exists via vectors related to failed login attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2064
- https://github.com/jenkinsci/jenkins/commit/fbf96734470caba9364f04e0b77b0bae7293a1ec
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://www.openwall.com/lists/oss-security/2014/02/21/2
