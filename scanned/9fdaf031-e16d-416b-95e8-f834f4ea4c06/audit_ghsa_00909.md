# [H] Improper Authorization in loopback

## Summary
Severity: High
Advisory: GHSA-8wgc-jjvv-cv6v
CWE: CWE-285
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-8wgc-jjvv-cv6v
Type: github-advisory

## Affected
- npm: `loopback` — affected >=0 <2.40.0
- npm: `loopback` — affected >=3.0.0 <3.22.0

## Details
Vulnerable versions of `loopback` may allow attackers to create Authentication Tokens on behalf of other users due to Improper Authorization. If the AccessToken model is publicly exposed, an attacker can create Authorization Tokens for any user as long as they know the target's `userId`. This will allow the attacker to access the user's data and their privileges.


## Recommendation

For loopback 2.x, upgrade to version 2.40.0 or later
For loopback 3.x, upgrade to version 3.22.0 or later

## References
- https://github.com/strongloop/loopback
- https://loopback.io/doc/en/lb2/Security-advisory-08-08-2018.html]
- https://loopback.io/doc/en/lb3/Security-advisory-08-08-2018.html]
- https://www.npmjs.com/advisories/771
