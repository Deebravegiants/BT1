# [C] samlify SAML Signature Wrapping attack

## Summary
Severity: Critical
Advisory: GHSA-r683-v43c-6xqv
CVE: CVE-2025-47949
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-r683-v43c-6xqv
Type: github-advisory

## Affected
- npm: `samlify` — affected >=0 <2.10.0

## Details
A Signature Wrapping attack has been found in samlify <v2.10.0, allowing an attacker to forge a SAML Response to authenticate as any user. 
An attacker would need a signed XML document by the identity provider.

## References
- https://github.com/tngan/samlify/security/advisories/GHSA-r683-v43c-6xqv
- https://nvd.nist.gov/vuln/detail/CVE-2025-47949
- https://github.com/tngan/samlify/commit/115679acd89f0a37ea3ebd8fff7db54fca3e8af3
- https://github.com/tngan/samlify
