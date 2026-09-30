# [C] Node-SAML SAML Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-m837-g268-mmv7
CVE: CVE-2025-54369
CWE: CWE-287, CWE-347, CWE-87
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-25
Source: https://github.com/advisories/GHSA-m837-g268-mmv7
Type: github-advisory

## Affected
- npm: `node-saml` — affected >=0
- npm: `@node-saml/node-saml` — affected >=0 <5.1.0

## Details
Node-SAML loads the assertion from the (unsigned) original response document. This is different than the parts that are verified when checking signature. 

This allows an attacker to modify authentication details within a valid SAML assertion. For example, in one attack it is possible to remove any character from the SAML assertion username.

To conduct the attack an attacker would need a validly signed document from the identity provider (IdP).

In fixing this we upgraded xml-crypto to v6.1.2 and made sure to process the SAML assertions from only verified/authenticated contents. This will prevent future variants from coming up.

## References
- https://github.com/node-saml/node-saml/security/advisories/GHSA-m837-g268-mmv7
- https://nvd.nist.gov/vuln/detail/CVE-2025-54369
- https://github.com/node-saml/node-saml/commit/31ead9411ebc3e2385086fa9149b6c17732bca10
- https://github.com/node-saml/node-saml
- https://github.com/node-saml/node-saml/releases/tag/v5.1.0
