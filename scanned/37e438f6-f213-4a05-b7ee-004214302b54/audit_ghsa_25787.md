# [M] Missing permission Jenkins Pipeline Phoenix AutoTest Plugin

## Summary
Severity: Medium
Advisory: GHSA-4c7h-f2j9-9c46
CVE: CVE-2022-28158
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-4c7h-f2j9-9c46
Type: github-advisory

## Affected
- Maven: `com.surenpi.jenkins:phoenix-autotest` — affected >=0

## Details
A missing permission check in Jenkins Pipeline: Phoenix AutoTest Plugin 1.3 and earlier allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28158
- https://github.com/jenkinsci/phoenix-autotest-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2685
- http://www.openwall.com/lists/oss-security/2022/03/29/1
