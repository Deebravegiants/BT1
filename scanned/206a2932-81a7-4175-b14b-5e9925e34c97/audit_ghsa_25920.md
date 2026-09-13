# [M] Arbitrary file read vulnerability in Jenkins kubernetes-cd Plugin

## Summary
Severity: Medium
Advisory: GHSA-fpxq-w7p9-r924
CVE: CVE-2022-27208
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-fpxq-w7p9-r924
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:kubernetes-cd` — affected >=0

## Details
Jenkins Kubernetes Continuous Deploy Plugin 2.3.1 and earlier allows users with Credentials/Create permission to read arbitrary files on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27208
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2096
- http://www.openwall.com/lists/oss-security/2022/03/15/2
