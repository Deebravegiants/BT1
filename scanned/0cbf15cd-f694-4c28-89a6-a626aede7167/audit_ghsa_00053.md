# [H] Samlify vulnerable to Authentication Bypass by allowing tokens to be reused with different usernames

## Summary
Severity: High
Advisory: GHSA-8jjf-w7j6-323c
CVE: CVE-2017-1000452
CWE: CWE-347, CWE-91
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-01-04
Source: https://github.com/advisories/GHSA-8jjf-w7j6-323c
Type: github-advisory

## Affected
- npm: `samlify` — affected >=0 <2.4.0-rc5

## Details
Versions of `samlify` prior to 2.4.0-rc5 are vulnerable to Authentication Bypass. The package fails to prevent XML Signature Wrapping, allowing tokens to be reused with different usernames. A remote attacker can modify SAML content for a SAML service provider without invalidating the cryptographic signature, which may allow attackers to bypass primary authentication for the affected SAML service provider.


## Recommendation

Upgrade to version 2.4.0-rc5 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000452
- https://github.com/tngan/samlify/commit/d382bbc7c6b8ea889839ae1f178730c25b09eb42
- https://hackerone.com/reports/356284
- https://github.com/tngan/samlify
- https://github.com/tngan/samlify/compare/v2.4.0-rc4...v2.4.0-rc5
- https://github.com/tngan/samlify/releases/tag/v2.4.0-rc5
- https://www.whitehats.nl/blog/xml-signature-wrapping-samlify
