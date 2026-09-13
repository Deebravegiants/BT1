# [M] Missing permission checks in MongoDB Plugin

## Summary
Severity: Medium
Advisory: GHSA-c26h-8h4p-4jgj
CVE: CVE-2020-2267
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c26h-8h4p-4jgj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mongodb` — affected >=0

## Details
A missing permission check in Jenkins MongoDB Plugin 1.3 and earlier allows attackers with Overall/Read permission to gain access to some metadata of any arbitrary files on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2267
- https://github.com/jenkinsci/mongodb-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1904
- http://www.openwall.com/lists/oss-security/2020/09/16/3
