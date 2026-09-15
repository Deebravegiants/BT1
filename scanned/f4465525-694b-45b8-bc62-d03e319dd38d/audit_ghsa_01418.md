# [C] Improper Authorization in react-oauth-flow

## Summary
Severity: Critical
Advisory: GHSA-65m9-m259-7jqw
CWE: CWE-285
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-65m9-m259-7jqw
Type: github-advisory

## Affected
- npm: `react-oauth-flow` — affected >=0.0.0

## Details
All versions of `react-oauth-flow` fail to properly implement the OAuth protocol. The package stores secrets in the front-end code. Instead of using a public OAuth client, it uses a confidential client on the browser. This may allow attackers to compromise server credentials.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://github.com/ethereum/web3.js/issues/2739
- https://github.com/ethereum/web3.js
- https://www.npmjs.com/advisories/1487
