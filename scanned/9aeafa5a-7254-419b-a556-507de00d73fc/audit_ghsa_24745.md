# [M] Stored XSS vulnerability in Jenkins REST List Parameter Plugin

## Summary
Severity: Medium
Advisory: GHSA-x3m6-vcp7-98mr
CVE: CVE-2021-21635
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x3m6-vcp7-98mr
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:rest-list-parameter` — affected >=0 <1.3.1

## Details
Jenkins REST List Parameter Plugin 1.3.0 and earlier does not escape a parameter name reference in embedded JavaScript.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Jenkins REST List Parameter Plugin 1.3.1 no longer identifies a parameter using user-specified content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21635
- https://github.com/jenkinsci/rest-list-parameter-plugin/commit/ff4bb2b44eb05b35bfb68a3a63ac7c5e72cb96b6
- https://github.com/jenkinsci/rest-list-parameter-plugin
- https://www.jenkins.io/security/advisory/2021-03-30/#SECURITY-2261
- http://www.openwall.com/lists/oss-security/2021/03/30/1
