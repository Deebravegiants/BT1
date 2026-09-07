# [H] Improper Authorization in googleapis

## Summary
Severity: High
Advisory: GHSA-7543-mr7h-6v86
CWE: CWE-285
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-7543-mr7h-6v86
Type: github-advisory

## Affected
- npm: `googleapis` — affected >=0 <39.1.0

## Details
Versions of `googleapis` prior to 39.1.0 are vulnerable to Improper Authorization. Setting credentials to one client may apply to all clients which may cause requests to be sent with the incorrect credentials.


## Recommendation

Upgrade to version 39.1.0.

## References
- https://github.com/googleapis/google-api-nodejs-client/issues/1594
- https://github.com/googleapis/google-api-nodejs-client
- https://www.npmjs.com/advisories/791
