# [M] Improper Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-4h47-h3cr-23wh
CVE: CVE-2018-1000408
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4h47-h3cr-23wh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.138.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.140 <2.146

## Details
A denial of service vulnerability exists in Jenkins 2.145 and earlier, LTS 2.138.1 and earlier in core/src/main/java/hudson/security/HudsonPrivateSecurityRealm.java that allows attackers without Overall/Read permission to access a specific URL on instances using the built-in Jenkins user database security realm that results in the creation of an ephemeral user record in memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000408
- https://github.com/jenkinsci/jenkins/commit/01157a699f611ca7492e872103ac01526a982cf2
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-10-10/#SECURITY-1128
- http://www.securityfocus.com/bid/106532
