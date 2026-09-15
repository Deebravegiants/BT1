# [H] Message Signature Bypass in openpgp

## Summary
Severity: High
Advisory: GHSA-qwqc-28w3-fww6
CVE: CVE-2019-9153
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-08-23
Source: https://github.com/advisories/GHSA-qwqc-28w3-fww6
Type: github-advisory

## Affected
- npm: `openpgp` — affected >=0 <4.2.0

## Details
Versions of `openpgp` prior to 4.2.0 are vulnerable to Message Signature Bypass. The package fails to verify that a message signature is of type `text`. This allows an attacker to to construct a message with a signature type that only verifies subpackets without additional input (such as `standalone` or `timestamp`). For example, an attacker that captures a `standalone` signature packet from a victim can construct arbitrary signed messages that would be verified correctly.


## Recommendation

Upgrade to version 4.2.0 or later.
If you are upgrading from a version <4.0.0 it is highly recommended to read the `High-Level API Changes` section of the `openpgp` 4.0.0 release: https://github.com/openpgpjs/openpgpjs/releases/tag/v4.0.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9153
- https://github.com/openpgpjs/openpgpjs/pull/797/commits/327d3e5392a6f59a4270569d200c7f7a2bfc4cbc
- https://github.com/openpgpjs/openpgpjs/pull/816
- https://github.com/openpgpjs/openpgpjs/releases/tag/v4.2.0
- https://sec-consult.com/en/blog/advisories/multiple-vulnerabilities-in-openpgp-js
- https://snyk.io/vuln/SNYK-JS-OPENPGP-460248
- https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/Studies/Mailvelope_Extensions/Mailvelope_Extensions_pdf.html#download=1
- https://www.npmjs.com/advisories/1160
- http://packetstormsecurity.com/files/154191/OpenPGP.js-4.2.0-Signature-Bypass-Invalid-Curve-Attack.html
