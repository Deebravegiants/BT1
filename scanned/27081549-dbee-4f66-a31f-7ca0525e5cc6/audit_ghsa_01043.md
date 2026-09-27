# [H] Prototype Pollution in handlebars

## Summary
Severity: High
Advisory: GHSA-g9r4-xpmj-mj65
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-g9r4-xpmj-mj65
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=0 <3.0.8
- npm: `handlebars` — affected >=4.0.0 <4.5.3

## Details
Versions of `handlebars` prior to 3.0.8 or 4.5.3 are vulnerable to prototype pollution. It is possible to add or modify properties to the Object prototype through a malicious template. This may allow attackers to crash the application or execute Arbitrary Code in specific conditions.


## Recommendation

Upgrade to version 3.0.8, 4.5.3 or later.

## References
- https://www.npmjs.com/advisories/1325
