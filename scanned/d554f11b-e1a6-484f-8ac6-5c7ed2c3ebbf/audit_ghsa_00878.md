# [H] Command Injection in local-devices

## Summary
Severity: High
Advisory: GHSA-w725-67p7-xv22
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-w725-67p7-xv22
Type: github-advisory

## Affected
- npm: `local-devices` — affected >=0 <3.0.0

## Details
Versions of `local-devices` prior to 3.0.0 are vulnerable to Command Injection. The package does not validate input on ip addresses and concatenates it to an exec call, allowing attackers to run arbitrary commands in the system.


## Recommendation

Upgrade to version 3.0.0 or later.

## References
- https://github.com/DylanPiercey/local-devices/pull/16
- https://github.com/DylanPiercey/local-devices/commit/57b9a933c9d23d34bd5a055536db824de66db553
- https://github.com/DylanPiercey/local-devices
- https://www.npmjs.com/advisories/1020
