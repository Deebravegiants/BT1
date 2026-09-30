# [H] Improper Authorization in @sap-cloud-sdk/core

## Summary
Severity: High
Advisory: GHSA-r2vw-jgq9-jqx2
CWE: CWE-285
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-r2vw-jgq9-jqx2
Type: github-advisory

## Affected
- npm: `@sap-cloud-sdk/core` — affected >=1.19.0 <1.21.2

## Details
Affected versions of `@sap-cloud-sdk/core` do not properly validate JWTs.  The `verifyJwt()` function does not properly validate the URL from where the public verification key for the JWT can be downloaded.  Any URL was trusted which makes it possible to provide a URL belonging to a manipulated JWT.


## Recommendation

Upgrade to version 1.21.2 or later.

## References
- https://www.npmjs.com/advisories/1540
