# [M] Missing Authorization in Jenkins Mercurial Plugin

## Summary
Severity: Medium
Advisory: GHSA-vrrc-3wwh-frgx
CVE: CVE-2020-2306
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vrrc-3wwh-frgx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=2.11 <2.12
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=2.10 <2.10.1
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=2.9 <2.9.1
- Maven: `org.jenkins-ci.plugins:mercurial` — affected >=0 <2.8.1

## Details
Mercurial Plugin prior to 2.12, 2.10.1, 2.9.1, and 2.8.1 does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to obtain a list of names of configured Mercurial installations.

Mercurial Plugin 2.12, 2.10.1, 2.9.1, and 2.8.1 performs permission checks when listing configured Mercurial installations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2306
- https://github.com/jenkinsci/mercurial-plugin/commit/edd59db1eec7e3c8d467372cd8417ae65eeb29dd
- https://github.com/CVEProject/cvelist/blob/381fe967666a5ce01625a7a050427aa4757e3ca6/2020/2xxx/CVE-2020-2306.json
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2104
