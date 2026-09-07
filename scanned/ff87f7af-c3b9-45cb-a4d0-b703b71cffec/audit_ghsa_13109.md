# [M] XSS vulnerability in Jenkins Job Configuration History Plugin

## Summary
Severity: Medium
Advisory: GHSA-5jxp-f5rr-g6jc
CVE: CVE-2023-41931
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-5jxp-f5rr-g6jc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jobConfigHistory` — affected >=0 <1229.v3039470161a_d

## Details
Jenkins Job Configuration History Plugin 1227.v7a_79fc4dc01f and earlier does not property sanitize or escape the timestamp value from history entries when rendering a history entry on the history view, resulting in a stored cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41931
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3233
- http://www.openwall.com/lists/oss-security/2023/09/06/9
