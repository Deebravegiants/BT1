# [C] Authentication Bypass in express-laravel-passport

## Summary
Severity: Critical
Advisory: GHSA-v66p-w7qx-wv98
CWE: CWE-287
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-v66p-w7qx-wv98
Type: github-advisory

## Affected
- npm: `express-laravel-passport` — affected >=0.0.0

## Details
All versions of `express-laravel-passport` are vulnerable to an Authentication Bypass. The package fails to properly validate JWTs, allowing attackers to send HTTP requests impersonating other users.


## Recommendation

Upgrade to version 2.0.5 or later.

## References
- https://hackerone.com/reports/748214
- https://www.npmjs.com/advisories/1450
