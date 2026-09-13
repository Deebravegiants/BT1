# [H] Authentication Bypass in otpauth

## Summary
Severity: High
Advisory: GHSA-rmmc-8cqj-hfp3
CWE: CWE-287
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-rmmc-8cqj-hfp3
Type: github-advisory

## Affected
- npm: `otpauth` — affected >=0 <3.2.8

## Details
Versions of `otpauth` prior to 3.2.8 are vulnerable to Authentication Bypass. The package's `totp.validate()` function may return positive values for single digit tokens even if they are invalid. This may allow attackers to bypass the OTP authentication by providing single digit tokens.


## Recommendation

Upgrade to version 3.2.8 or later.

## References
- https://www.npmjs.com/advisories/1087
