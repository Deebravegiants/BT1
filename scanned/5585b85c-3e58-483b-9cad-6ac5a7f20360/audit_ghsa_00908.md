# [H] Command Injection in soletta-dev-app

## Summary
Severity: High
Advisory: GHSA-8mgg-5x65-m4m4
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-8mgg-5x65-m4m4
Type: github-advisory

## Affected
- npm: `soletta-dev-app` — affected >=0

## Details
All versions of `soletta-dev-app` are vulnerable to Command Injection. The package does not validate user input on the `/api/service/status` API endpoint, passing contents of the `service` query parameter to an exec call. This may allow attackers to run arbitrary commands in the system.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/958
