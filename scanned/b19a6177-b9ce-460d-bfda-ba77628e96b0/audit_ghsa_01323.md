# [C] Command Injection in samsung-remote

## Summary
Severity: Critical
Advisory: GHSA-xhjx-mfr6-9rr4
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-xhjx-mfr6-9rr4
Type: github-advisory

## Affected
- npm: `samsung-remote` — affected >=0 <1.3.5

## Details
Versions of `samsung-remote` before 1.3.5 are vulnerable to command injection. This vulnerability is exploitable if user input is passed into the `ip` option of the package constructor.


## Recommendation

Update to version 1.3.5 or later.

## References
- https://hackerone.com/reports/394294
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/465.json
- https://www.npmjs.com/advisories/734
