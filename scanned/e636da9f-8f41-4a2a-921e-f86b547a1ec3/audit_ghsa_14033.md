# [M] Jenkins SAML Single Sign On(SSO) Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ghpm-mgf5-cv8q
CVE: CVE-2023-32995
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-ghpm-mgf5-cv8q
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:miniorange-saml-sp` — affected >=0 <2.0.1

## Details
Jenkins SAML Single Sign On(SSO) Plugin 2.0.0 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to send an HTTP POST request with JSON body containing attacker-specified content, to miniOrange’s API for sending emails.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

SAML Single Sign On(SSO) Plugin 2.0.1 removes the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32995
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2994
