# [M] XXE vulnerability in Jenkins Mercurial Plugin

## Summary
Severity: Medium
Advisory: GHSA-x58r-wxc3-7pqr
CVE: CVE-2020-2305
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x58r-wxc3-7pqr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=2.11 <2.12
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=2.10 <2.10.1
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=2.9 <2.9.1
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=0 <2.8.1

## Details
Jenkins Mercurial Plugin prior to 2.12, 2.10.1, 2.9.1, and 2.8.1 does not configure its XML changelog parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control an agent process to have Jenkins parse a crafted changelog file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Mercurial Plugin 2.12, 2.10.1, 2.9.1, and 2.8.1 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2305
- https://github.com/jenkinsci/mercurial-plugin/commit/84af58b08f80bb92792f7bc04a31487f3eeee95a
- https://github.com/CVEProject/cvelist/blob/381fe967666a5ce01625a7a050427aa4757e3ca6/2020/2xxx/CVE-2020-2305.json
- https://github.com/jenkinsci/mercurial-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2115
