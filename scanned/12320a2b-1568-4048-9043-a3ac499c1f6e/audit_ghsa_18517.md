# [C] Node-SAML SAML Signature Verification Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4mxg-3p6v-xgq3
CVE: CVE-2025-54419
CWE: CWE-287, CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-07-28
Source: https://github.com/advisories/GHSA-4mxg-3p6v-xgq3
Type: github-advisory

## Affected
- npm: `@node-saml/node-saml` — affected >=0 <5.1.0
- npm: `passport-saml` — affected >=0
- npm: `@node-saml/passport-saml` — affected >=0 <5.1.0

## Details
Node-SAML loads the assertion from the (unsigned) original response document. This is different than the parts that are verified when checking signature.

This allows an attacker to modify authentication details within a valid SAML assertion. For example, in one attack it is possible to remove any character from the SAML assertion username.

To conduct the attack an attacker would need a validly signed document from the identity provider (IdP).

In fixing this we made sure to process the SAML assertions from only verified/authenticated contents. This will prevent future variants from coming up. 

Note: this is distinct from the previous xml-crypto CVEs.

## References
- https://github.com/node-saml/node-saml/security/advisories/GHSA-4mxg-3p6v-xgq3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54419
- https://github.com/node-saml/node-saml/commit/31ead9411ebc3e2385086fa9149b6c17732bca10
- https://github.com/node-saml/node-saml
- https://github.com/node-saml/node-saml/releases/tag/v5.1.0
