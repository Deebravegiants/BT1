# [C] Forgeable Public/Private Tokens in jwt-simple

## Summary
Severity: Critical
Advisory: GHSA-vgrx-w6rg-8fqf
CVE: CVE-2016-10555
CWE: CWE-20
Ecosystem: npm
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-vgrx-w6rg-8fqf
Type: github-advisory

## Affected
- npm: `jwt-simple` — affected >=0 <0.3.1

## Details
Affected versions of the `jwt-simple` package allow users to select what algorithm the server will use to verify a provided JWT. A malicious actor can use this behaviour to arbitrarily modify the contents of a JWT while still passing verification. For the common use case of the JWT, the end result is a complete authentication bypass with minimal effort.



## Recommendation

Update to version 0.3.1 or later.

Additionally, be sure to always specify an algorithm in calls to `.decode()`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10555
- https://github.com/hokaccha/node-jwt-simple/pull/14
- https://github.com/hokaccha/node-jwt-simple/pull/16
- https://github.com/hokaccha/node-jwt-simple/commit/957957cfa44474049b4603b293569588ee9ffd97
- https://auth0.com/blog/2015/03/31/critical-vulnerabilities-in-json-web-token-libraries
- https://www.npmjs.com/advisories/87
