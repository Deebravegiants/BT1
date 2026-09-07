# [M] Cross-site Scripting in Jenkins Random String Parameter Plugin

## Summary
Severity: Medium
Advisory: GHSA-38w4-q97c-xh4x
CVE: CVE-2022-30966
CWE: CWE-116, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-38w4-q97c-xh4x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:random-string-parameter` — affected >=0

## Details
Jenkins Random String Parameter Plugin 1.0 and earlier does not escape the name and description of Random String parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30966
- https://github.com/jenkinsci/random-string-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2717
