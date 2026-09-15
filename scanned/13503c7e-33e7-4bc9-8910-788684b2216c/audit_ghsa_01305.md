# [H] Sensitive Data Exposure in rails-session-decoder

## Summary
Severity: High
Advisory: GHSA-44vf-8ffm-v2qh
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-44vf-8ffm-v2qh
Type: github-advisory

## Affected
- npm: `rails-session-decoder` — affected >=0.0.0

## Details
All versions of `rails-session-decoder` are missing verification of the Message Authentication Code appended to the cookies. This may lead to decryption of cipher text thus exposing encrypted information.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/753
