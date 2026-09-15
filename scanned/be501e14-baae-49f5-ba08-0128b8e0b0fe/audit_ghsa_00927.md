# [C] Arbitrary Code Execution in require-node

## Summary
Severity: Critical
Advisory: GHSA-8j6j-4h2c-c65p
CWE: CWE-78
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-8j6j-4h2c-c65p
Type: github-advisory

## Affected
- npm: `require-node` — affected >=0 <1.3.4
- npm: `require-node` — affected >=2.0.0 <2.0.4

## Details
Versions of `require-node` prior to 1.3.4 for 1.x and 2.0.4 for 2.x are vulnerable to Arbitrary Code Execution. The package fails to sanitize requests to the `require-node` endpoint, allowing attackers to execute arbitrary code in the server through the injection of OS commands in the request body.


## Recommendation

- If you are using 1.x, upgrade to version 1.3.4 or later.
- If you are using 2.x, upgrade to version 2.0.4 or later.

## References
- https://www.npmjs.com/advisories/1015
