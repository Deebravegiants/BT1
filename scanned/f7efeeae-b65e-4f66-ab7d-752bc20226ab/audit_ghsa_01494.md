# [M] Buffer Overflow in node-weakauras-parser

## Summary
Severity: Medium
Advisory: GHSA-86mr-6m89-vgj3
CWE: CWE-120
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-86mr-6m89-vgj3
Type: github-advisory

## Affected
- npm: `node-weakauras-parser` — affected >=1.0.4 <1.0.5
- npm: `node-weakauras-parser` — affected >=2.0.0 <2.0.2
- npm: `node-weakauras-parser` — affected >=3.0.0 <3.0.1

## Details
Affected versions of `node-weakauras-parser` are vulnerable to a Buffer Overflow. The `encode_weakaura` function fails to properly validate the input size. A buffer of 13835058055282163711 bytes causes an overflow on 64-bit systems.


## Recommendation

Upgrade to versions 1.0.5, 2.0.2, 3.0.1 or later.

## References
- https://github.com/Zireael-N/node-weakauras-parser/commit/bc146da09db689e554d28e948f1cf1c138f09f69#diff-023afe6291ac9ada88788108cb3367b3R38-R43
- https://github.com/Zireael-N/node-weakauras-parser
- https://www.npmjs.com/advisories/1504
