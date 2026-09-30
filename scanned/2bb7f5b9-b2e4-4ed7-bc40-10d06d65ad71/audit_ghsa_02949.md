# [H] Insufficient Session Expiration in @cyyynthia/tokenize

## Summary
Severity: High
Advisory: GHSA-jcjx-c3j3-44pr
CWE: CWE-613
Ecosystem: npm
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-jcjx-c3j3-44pr
Type: github-advisory

## Affected
- npm: `@cyyynthia/tokenize` — affected >=1.1.0 <1.1.3

## Details
### Impact
A bug introduced in version 1.1.0 made Tokenize generate faulty tokens with NaN as a generation date. As a result, tokens would not properly expire and remain valid regardless of the `lastTokenReset` field.

### Patches
Version 1.1.3 contains a patch that'll invalidate these faulty tokens and make new ones behave as expected.

### Workarounds
None. Tokens do not hold the necessary information to perform invalidation anymore.

### References
PR #1

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/cyyynthia/tokenize](https://github.com/cyyynthia/tokenize)
* Email us at [cynthia@cynthia.dev](mailto:cynthia@cynthia.dev)

## References
- https://github.com/cyyynthia/tokenize/security/advisories/GHSA-jcjx-c3j3-44pr
- https://github.com/cyyynthia/tokenize
