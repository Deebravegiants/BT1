# [M] Jenkins SAML Single Sign On(SSO) Plugin unconditionally disables SSL/TLS certificate validation

## Summary
Severity: Medium
Advisory: GHSA-9m92-qwpc-qm78
CVE: CVE-2023-32994
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-9m92-qwpc-qm78
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:miniorange-saml-sp` — affected >=0 <2.2.0

## Details
Jenkins SAML Single Sign On(SSO) Plugin 2.1.0 and earlier unconditionally disables SSL/TLS certificate validation for connections to miniOrange or the configured IdP to retrieve SAML metadata.

This lack of validation could be abused using a man-in-the-middle attack to intercept these connections.

SAML Single Sign On(SSO) Plugin 2.2.0 performs SSL/TLS certificate validation when connecting to miniOrange or the configured IdP to retrieve SAML metadata.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32994
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3001%20(2)
