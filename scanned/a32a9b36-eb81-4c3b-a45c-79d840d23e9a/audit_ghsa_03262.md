# [C] Signature Validation Bypass

## Summary
Severity: Critical
Advisory: GHSA-5684-g483-2249
CWE: CWE-347
Ecosystem: Go
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-5684-g483-2249
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.5.0

## Details
### Impact
Given a valid SAML Response, an attacker can potentially modify the document, bypassing signature validation in order to pass off the altered document as a signed one.

This enables a variety of attacks, including users accessing accounts other than the one to which they authenticated in the identity provider, or full authentication bypass if an external attacker can obtain an expired, signed SAML Response.

### Patches
A patch is available, users of gosaml2 should upgrade to v0.5.0 or higher.

### References
See the [underlying advisory on goxmldsig](https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7) for more details.

## References
- https://github.com/russellhaering/gosaml2/security/advisories/GHSA-5684-g483-2249
- https://github.com/russellhaering/gosaml2
