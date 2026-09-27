# [H] Signature Verification Bypass in jwt-simple

## Summary
Severity: High
Advisory: GHSA-8v5f-hp78-jgxq
CWE: CWE-347
Ecosystem: npm
Published: 2019-06-06
Source: https://github.com/advisories/GHSA-8v5f-hp78-jgxq
Type: github-advisory

## Affected
- npm: `jwt-simple` — affected >=0 <0.5.3

## Details
Versions of `jwt-simple` prior to 0.5.3 are vulnerable to Signature Verification Bypass. If no algorithm is specified in the `decode()` function, the packages uses the algorithm in the JWT to decode tokens. This allows an attacker to create a HS256 (symmetric algorithm) JWT with the server's public key as secret, and the package will verify it as HS256 instead of RS256 (asymmetric algorithm).


## Recommendation

Upgrade to version 0.5.3 or later.

## References
- https://github.com/hokaccha/node-jwt-simple/commit/ead36e1d687645da9c3be8befdaaef622ea33106
- https://www.npmjs.com/advisories/831
