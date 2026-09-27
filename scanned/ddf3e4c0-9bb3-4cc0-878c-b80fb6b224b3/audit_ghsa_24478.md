# [M] Incorrect Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-wmr8-25ff-ggpj
CVE: CVE-2018-1999004
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wmr8-25ff-ggpj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.121.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.122 <2.132

## Details
A Improper authorization vulnerability exists in Jenkins 2.132 and earlier, 2.121.1 and earlier in SlaveComputer.java that allows attackers with Overall/Read permission to initiate agent launches, and abort in-progress agent launches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999004
- https://github.com/jenkinsci/jenkins/commit/40250f08aca7f3f8816f21870ee23463a52ef2f2
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-07-18/#SECURITY-892
- https://www.oracle.com/security-alerts/cpuapr2022.html
