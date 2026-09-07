# [M] Jenkins Fortify Plugin HTML injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-223m-pgcq-f3xg
CVE: CVE-2023-4303
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-08-22
Source: https://github.com/advisories/GHSA-223m-pgcq-f3xg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify` — affected >=0 <22.2.39

## Details
Jenkins Fortify Plugin 22.1.38 and earlier does not escape the error message for a form validation method. This results in an HTML injection vulnerability.

Fortify Plugin 22.2.39 removes HTML tags from the error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4303
- https://github.com/jenkinsci/fortify-plugin/commit/357d7bfbcb0ff796ea7d078bee13159f1d000f5d
- https://github.com/jenkinsci/fortify-plugin
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3140
