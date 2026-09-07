# [H] Jenkins Coverity Plugin vulnerable to cross-site request forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-5x3f-7m52-9cgf
CVE: CVE-2022-36920
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-5x3f-7m52-9cgf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:coverity` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Coverity Plugin 1.11.4 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36920
- https://github.com/jenkinsci/coverity-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2790%20(2)
- http://www.openwall.com/lists/oss-security/2022/07/27/1
