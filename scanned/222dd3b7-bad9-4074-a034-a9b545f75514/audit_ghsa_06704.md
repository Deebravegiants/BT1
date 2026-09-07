# [H] SimpleSAMLphp SP accepts a response from an unexpected IdP when unsigned `Response/InResponseTo` is combined with a signed assertion lacking `SubjectConfirmationData/InResponseTo`

## Summary
Severity: High
Advisory: GHSA-q8r6-xj3f-wrrm
CVE: CVE-2026-49284
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-q8r6-xj3f-wrrm
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=2.5.0 <2.5.2
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <2.4.7

## Details
## Summary

SimpleSAMLphp's SAML SP ACS path does not enforce the IdP selected for an SP-initiated login. If a saved SP state contains `ExpectedIssuer = IdP A`, but the ACS receives a valid response from `IdP B`, the code logs a warning and continues processing instead of rejecting the response.

That behavior becomes security-relevant when combined with the response-processing rule that accepts an unsigned `samlp:Response/@InResponseTo` outside the signed assertion whenever the signed assertion's `SubjectConfirmationData` does not carry its own `InResponseTo`. A response issued by one trusted IdP can therefore be bound to SP state created for another IdP.

## Impact

In a multi-IdP deployment, a lower-trust IdP can satisfy SP state created for a different expected IdP. This can bypass an SP flow that intentionally routes the user to a specific IdP, including deployments that set `enable_unsolicited` to `false` to prevent IdP-initiated logins.

The impact is highest when the SP trusts multiple IdPs with different assurance levels, tenant boundaries, or attribute namespaces, and application authorization depends on the selected/expected IdP. In those deployments this is an authentication/authorization bypass candidate. Impact strongly depends on whether an attacker can obtain a signed IdP-initiated assertion from a lower-trust trusted IdP and whether the downstream application maps identifiers globally.

## References
- https://github.com/simplesamlphp/simplesamlphp/security/advisories/GHSA-q8r6-xj3f-wrrm
- https://github.com/simplesamlphp/simplesamlphp
