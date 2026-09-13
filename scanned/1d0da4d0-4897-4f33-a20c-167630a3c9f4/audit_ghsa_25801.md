# [M] Path traversal in Jenkins Pipeline Phoenix AutoTest Plugin

## Summary
Severity: Medium
Advisory: GHSA-62hc-f8qj-5xc3
CVE: CVE-2022-28157
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-62hc-f8qj-5xc3
Type: github-advisory

## Affected
- Maven: `com.surenpi.jenkins:phoenix-autotest` — affected >=0

## Details
Jenkins Pipeline: Phoenix AutoTest Plugin 1.3 and earlier allows attackers with Item/Configure permission to upload arbitrary files from the Jenkins controller via FTP to an attacker-specified FTP server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28157
- https://github.com/jenkinsci/phoenix-autotest-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2684
- http://www.openwall.com/lists/oss-security/2022/03/29/1
