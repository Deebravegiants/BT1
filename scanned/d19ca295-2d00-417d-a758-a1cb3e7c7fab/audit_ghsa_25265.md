# [M] Cross-site scripting vulnerability exists in Jenkins and Stapler Plugin

## Summary
Severity: Medium
Advisory: GHSA-6456-xjm5-g3pg
CVE: CVE-2018-1999007
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6456-xjm5-g3pg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.121.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.122 <2.132
- Maven: `org.kohsuke.stapler:stapler-parent` — affected >=0 <1.250.1

## Details
A cross-site scripting vulnerability exists in Jenkins 2.132 and earlier, 2.121.1 and earlier in the Stapler web framework's org/kohsuke/stapler/Stapler.java that allows attackers with the ability to control the existence of some URLs in Jenkins to define JavaScript that would be executed in another user's browser when that other user views HTTP 404 error pages while Stapler debug mode is enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999007
- https://github.com/jenkinsci/stapler/commit/03e221a81e8424709d1fbdf72ab814309dd8e13f
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-07-18/#SECURITY-390
- https://www.oracle.com/security-alerts/cpuapr2022.html
