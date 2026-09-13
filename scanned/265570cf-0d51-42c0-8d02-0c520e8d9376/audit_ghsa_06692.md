# [H] SimpleSAMLphp has Possible DoS via XPath Transform

## Summary
Severity: High
Advisory: GHSA-5cjr-mxj5-wmrx
CVE: CVE-2026-49289
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-5cjr-mxj5-wmrx
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=4.20.0 <4.20.3
- Packagist: `simplesamlphp/saml2-legacy` — affected >=4.20.0 <4.20.3
- Packagist: `simplesamlphp/saml2` — affected >=0 <4.19.3
- Packagist: `simplesamlphp/saml2-legacy` — affected >=0 <4.19.3

## Details
## Summary

This library turned out to be vulnerable to Denial-of-Service attacks using XPath transforms. A mitigation has been put in place to restrict the number of transforms and to restrict transforms to only the transform-algorithms mentioned in the SAML 2.0 Core Specifications (and specifically refuse XPath transforms).

## Impact

An attacker is able to send specially crafted messages to any entity relying on SimpleSAMLphp (or directly on this SAML2-library) to be able to perform a Denial-of-Service attack.

## References
- https://github.com/simplesamlphp/saml2/security/advisories/GHSA-5cjr-mxj5-wmrx
- https://github.com/simplesamlphp/saml2
