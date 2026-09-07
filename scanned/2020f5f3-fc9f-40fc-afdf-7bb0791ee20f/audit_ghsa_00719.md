# [M] ECDSA signature vulnerability of Minerva timing attack in jsrsasign

## Summary
Severity: Medium
Advisory: GHSA-g753-jx37-7xwh
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2020-06-30
Source: https://github.com/advisories/GHSA-g753-jx37-7xwh
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=4.0.0 <8.0.13

## Details
### Impact
ECDSA side-channel attack named [Minerava](https://minerva.crocs.fi.muni.cz/) have been found and it was found that it affects to jsrsasign.

Execution time of thousands signature generation have been observed then EC private key which is scalar value may be recovered since point and scalar multiplication time depends on bits of scalar. In jsrsasign 8.0.13 or later, execution time of EC point and scalar multiplication is almost constant and fixed for the issue.

- Minerva is one of timing attack or side channel attack for EC.
- If you don't use ECDSA class, you are not affected the vulnerability.
- The vulnerability is that attacker may guess private key by checking processing time of EC key generation or ECDSA signing.
- The cause issue is that point multiplication processing time in ECDSA signing is depends on private key value.
- After 8.0.13, processing time of point multiplication in ECDSA signing have become constant for key value in theory.

### Patches
Users using ECDSA signature generation should upgrade to 8.0.13 or later.

### Workarounds
There is no workarounds in jsrsasign. Update jsrsasign or use other ECDSA library.

### ACKNOWLEDGEMENT
Thanks to Jan Jancar @J08nY, Petr Svenda and Vladimir Sedlacek of Masaryk University in Czech Republic to find and report this vulnerability.

### References
https://minerva.crocs.fi.muni.cz/
https://www.npmjs.com/advisories/1505
https://github.com/kjur/jsrsasign/issues/411

## References
- https://github.com/kjur/jsrsasign/security/advisories/GHSA-g753-jx37-7xwh
- https://github.com/kjur/jsrsasign/issues/411
- https://github.com/kjur/jsrsasign/commit/9dcb89c57408a3d4b5b66aa9138426bd92819e73
- https://github.com/kjur/jsrsasign
- https://github.com/kjur/jsrsasign/releases/tag/8.0.13
- https://minerva.crocs.fi.muni.cz
- https://snyk.io/vuln/SNYK-JS-JSRSASIGN-561755
- https://www.npmjs.com/advisories/1505
