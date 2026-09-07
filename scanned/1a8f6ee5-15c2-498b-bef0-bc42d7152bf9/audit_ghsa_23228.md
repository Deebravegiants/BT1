# [M] XSS vulnerability in Jenkins TICS Plugin

## Summary
Severity: Medium
Advisory: GHSA-xmw5-45v9-pxqx
CVE: CVE-2021-21613
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xmw5-45v9-pxqx
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:tics` — affected >=0 <2020.3.0.7

## Details
Jenkins TICS Plugin 2020.3.0.6 and earlier does not escape TICS service responses.

This results in a cross-site scripting (XSS) vulnerability exploitable by attackers able to control TICS service response content.

Jenkins TICS Plugin 2020.3.0.7 escapes TICS service responses, or strips HTML out, as appropriate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21613
- https://github.com/jenkinsci/tics-plugin/commit/a64493ccf81a241c5e51736721c4fe9a3e56622b
- https://github.com/jenkinsci/tics-plugin
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2098
