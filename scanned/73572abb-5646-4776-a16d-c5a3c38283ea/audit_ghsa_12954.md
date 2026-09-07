# [M] Jenkins Fortify Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3fjv-8r82-6xm9
CVE: CVE-2023-4301
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-22
Source: https://github.com/advisories/GHSA-3fjv-8r82-6xm9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify` — affected >=0 <22.2.39

## Details
Jenkins Fortify Plugin 22.1.38 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Fortify Plugin 22.2.39 requires POST requests and the appropriate permissions for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4301
- https://github.com/jenkinsci/fortify-plugin/commit/357d7bfbcb0ff796ea7d078bee13159f1d000f5d
- https://github.com/jenkinsci/fortify-plugin
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3115
