# [H] Improper Key Verification in openpgp

## Summary
Severity: High
Advisory: GHSA-hfmf-q43v-2ffj
CVE: CVE-2019-9154
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-08-23
Source: https://github.com/advisories/GHSA-hfmf-q43v-2ffj
Type: github-advisory

## Affected
- npm: `openpgp` — affected >=0 <4.2.0

## Details
Versions of `openpgp` prior to 4.2.0 are vulnerable to Improper Key Verification. The OpenPGP standard allows signature packets to have subpackets which may be hashed or unhashed. Unhashed subpackets are not cryptographically protected and cannot be trusted. The `openpgp` package does not verify whether a subpacket is hashed. Furthermore, due to the order of parsing a signature packet information from unhashed subpackets overwrites information from hashed subpackets. This may allow an attacker to modify the contents of a key certification signature or revocation signature. Doing so could convince a victim to use an obsolete key for encryption. An attack require a victim to import a manipulated key or update an existing key with a manipulated version.


## Recommendation

Upgrade to version 4.2.0 or later. 
If you are upgrading from a version <4.0.0 it is highly recommended to read the `High-Level API Changes` section of the `openpgp` 4.0.0 release: https://github.com/openpgpjs/openpgpjs/releases/tag/v4.0.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9154
- https://github.com/openpgpjs/openpgpjs/pull/797
- https://github.com/openpgpjs/openpgpjs/pull/797/commits/47138eed61473e13ee8f05931119d3e10542c5e1
- https://github.com/openpgpjs/openpgpjs/releases/tag/v4.2.0
- https://sec-consult.com/en/blog/advisories/multiple-vulnerabilities-in-openpgp-js
- https://snyk.io/vuln/SNYK-JS-OPENPGP-460247
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.html#download=1
- https://www.npmjs.com/advisories/1161
- http://packetstormsecurity.com/files/154191/OpenPGP.js-4.2.0-Signature-Bypass-Invalid-Curve-Attack.html
