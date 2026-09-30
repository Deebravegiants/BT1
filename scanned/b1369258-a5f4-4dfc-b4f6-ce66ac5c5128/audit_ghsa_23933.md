# [M] Incorrect Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-r2jf-rc5v-vmpv
CVE: CVE-2018-1999047
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r2jf-rc5v-vmpv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.121.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.122 <2.138

## Details
A improper authorization vulnerability exists in Jenkins 2.137 and earlier, 2.121.2 and earlier in UpdateCenter.java that allows attackers to cancel a Jenkins restart scheduled through the update center.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999047
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-08-15/#SECURITY-1076
