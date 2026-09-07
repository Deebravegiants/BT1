# [H] Command Injection in entitlements

## Summary
Severity: High
Advisory: GHSA-g8vp-6hv4-m67c
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-g8vp-6hv4-m67c
Type: github-advisory

## Affected
- npm: `entitlements` — affected >=0 <1.3.0

## Details
Versions of `entitlements` prior to 1.3.0 are vulnerable to Command Injection. The package does not validate input on the `entitlements` function  and concatenates it to an exec call, allowing attackers to run arbitrary commands in the system.


## Recommendation

Upgrade to version 1.3.0 or later.

## References
- https://hackerone.com/reports/341869
- https://www.npmjs.com/advisories/998
