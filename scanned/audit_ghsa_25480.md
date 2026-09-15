# [H]  Wizkunde SAMLBase SAML Bypass

## Summary
Severity: High
Advisory: GHSA-7gh2-8q93-87hp
CVE: CVE-2018-5387
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7gh2-8q93-87hp
Type: github-advisory

## Affected
- Packagist: `gogentooss/samlbase` — affected >=0 <1.2.7

## Details
Wizkunde SAMLBase may incorrectly utilize the results of XML DOM traversal and canonicalization APIs in such a way that an attacker may be able to manipulate the SAML data without invalidating the cryptographic signature, allowing the attack to potentially bypass authentication to SAML service providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5387
- https://github.com/GoGentoOSS/SAMLBase/issues/3
- https://github.com/GoGentoOSS/SAMLBase/commit/482cdf8c090e0f1179073034ebcb609ac7c3f5b3
- https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations
- https://github.com/GoGentoOSS/SAMLBase
- https://www.kb.cert.org/vuls/id/475445
