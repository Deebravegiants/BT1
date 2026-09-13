# [H] Command Injection in addax

## Summary
Severity: High
Advisory: GHSA-4q8f-5xxj-946r
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-4q8f-5xxj-946r
Type: github-advisory

## Affected
- npm: `addax` — affected >=0 <1.1.0

## Details
Versions of `addax` prior to 1.1.0 are vulnerable to Command Injection. The package does not validate user input on the `presignPath` function which receives input directly from the API endpoint. Exploiting the vulnerability requires authentication. This may allow attackers to run arbitrary commands in the system.


## Recommendation

Upgrade to version 1.1.0 or later.

## References
- https://www.npmjs.com/advisories/954
