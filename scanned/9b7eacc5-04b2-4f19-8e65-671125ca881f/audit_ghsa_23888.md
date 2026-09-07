# [M] Session Fixation in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-rr6r-p7rw-369c
CVE: CVE-2018-1000409
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rr6r-p7rw-369c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.138.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.140 <2.146

## Details
A session fixation vulnerability exists in Jenkins 2.145 and earlier, LTS 2.138.1 and earlier in core/src/main/java/hudson/security/HudsonPrivateSecurityRealm.java that prevented Jenkins from invalidating the existing session and creating a new one when a user signed up for a new user account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000409
- https://github.com/jenkinsci/jenkins/commit/517da6ed389f0a606dd9bb8595bc79fc93f4331c
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-10-10/#SECURITY-1158
- http://www.securityfocus.com/bid/106532
