# [C] Command Injection in command-exists

## Summary
Severity: Critical
Advisory: GHSA-cff4-rrq6-h78w
CWE: CWE-77
Ecosystem: npm
Published: 2019-06-03
Source: https://github.com/advisories/GHSA-cff4-rrq6-h78w
Type: github-advisory

## Affected
- npm: `command-exists` — affected >=0 <1.2.4

## Details
Versions of `command-exists` before 1.2.4 are vulnerable to command injection. This is exploitable if user input is provided to this module.


## Recommendation

Update to version 1.2.4 or later.

## References
- https://github.com/mathisonian/command-exists/commit/7ca91ba71604df6817a28c93d7776af9c49c431a
- https://hackerone.com/reports/324453
- https://github.com/mathisonian/command-exists/blob/v1.2.2/lib/command-exists.js#L49-L94
- https://www.npmjs.com/advisories/659
