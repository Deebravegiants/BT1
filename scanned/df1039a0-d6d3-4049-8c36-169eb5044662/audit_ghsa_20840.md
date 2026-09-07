# [H] secp256k1-js implements ECDSA without required r and s validation, leading to signature forgery

## Summary
Severity: High
Advisory: GHSA-q3f4-9h4p-vgr3
CVE: CVE-2022-41340
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-q3f4-9h4p-vgr3
Type: github-advisory

## Affected
- npm: `@lionello/secp256k1-js` — affected >=0 <1.1.0

## Details
The secp256k1-js package before 1.1.0 for Node.js implements ECDSA without required r and s validation, leading to signature forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41340
- https://github.com/lionello/secp256k1-js/issues/11
- https://github.com/lionello/secp256k1-js/commit/302800f0370b42e360a33774bb808274ac729c2e
- https://github.com/lionello/secp256k1-js
- https://github.com/lionello/secp256k1-js/compare/1.0.1...1.1.0
- https://www.npmjs.com/package/@lionello/secp256k1-js
