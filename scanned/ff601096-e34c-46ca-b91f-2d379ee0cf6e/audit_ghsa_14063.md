# [H] Double spend in snarkjs

## Summary
Severity: High
Advisory: GHSA-xp5g-jhg3-3rg2
CVE: CVE-2023-33252
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-xp5g-jhg3-3rg2
Type: github-advisory

## Affected
- npm: `snarkjs` — affected >=0

## Details
iden3 snarkjs through 0.6.11 allows double spending because there is no validation that the publicSignals length is less than the field modulus.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33252
- https://github.com/iden3/snarkjs
- https://github.com/iden3/snarkjs/commits/master/src/groth16_verify.js
- https://github.com/iden3/snarkjs/tags
