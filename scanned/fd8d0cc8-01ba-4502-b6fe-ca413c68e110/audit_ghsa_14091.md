# [M] Jenkins SAML Single Sign On(SSO) Plugin missing hostname validation

## Summary
Severity: Medium
Advisory: GHSA-6v6h-rw43-97fh
CVE: CVE-2023-32993
CWE: CWE-345, CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-6v6h-rw43-97fh
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:miniorange-saml-sp` — affected >=0 <2.1.0

## Details
Jenkins SAML Single Sign On(SSO) Plugin 2.0.2 and earlier does not perform hostname validation when connecting to miniOrange or the configured IdP to retrieve SAML metadata.

This lack of validation could be abused using a man-in-the-middle attack to intercept these connections.

SAML Single Sign On(SSO) Plugin 2.1.0 performs hostname validation when connecting to miniOrange or the configured IdP to retrieve SAML metadata.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32993
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3001%20(1)
