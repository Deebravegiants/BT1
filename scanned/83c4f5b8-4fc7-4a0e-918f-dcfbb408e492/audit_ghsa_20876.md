# [M] Missing hostname validation in Jenkins View26 Test-Reporting Plugin

## Summary
Severity: Medium
Advisory: GHSA-pxp5-g66h-wpv2
CVE: CVE-2022-41244
CWE: CWE-295, CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-pxp5-g66h-wpv2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:view26` — affected >=0

## Details
Jenkins View26 Test-Reporting Plugin 1.0.7 and earlier does not perform hostname validation when connecting to the configured View26 server that could be abused using a man-in-the-middle attack to intercept these connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41244
- https://github.com/jenkinsci/view26-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2069
