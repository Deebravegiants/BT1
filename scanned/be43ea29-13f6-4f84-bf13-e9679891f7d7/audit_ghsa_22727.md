# [M] Server-Side Request Forgery in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-6mv9-hcx5-7mhh
CVE: CVE-2018-1000067
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6mv9-hcx5-7mhh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.89.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.90 <2.107

## Details
An improper authorization vulnerability exists in Jenkins versions 2.106 and earlier, and LTS 2.89.3 and earlier, that allows an attacker to have Jenkins submit HTTP GET requests and get limited information about the response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000067
- https://github.com/jenkinsci/jenkins/commit/2d16b459205730d85e51499c2457109b234ca9d9
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-02-14/#SECURITY-506
- https://www.oracle.com/security-alerts/cpuapr2022.html
