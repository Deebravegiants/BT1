# [H] scheb/two-factor-bundle bypass two-factor authentication with unverified JWT trusted device token

## Summary
Severity: High
Advisory: GHSA-h6mp-mc7g-mg49
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-h6mp-mc7g-mg49
Type: github-advisory

## Affected
- Packagist: `scheb/two-factor-bundle` — affected >=3.0.0 <3.7.0

## Details
Before version 3.7 the bundle is vulnerable to a [security issue in JWT](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/), which can be exploited by an attacker to generate trusted device cookies on their own, effectively by-passing two-factor authentication.

## References
- https://github.com/scheb/two-factor-bundle/issues/143
- https://github.com/scheb/two-factor-bundle/commit/8890c1e47ae89e0ac6f8a40fd4bb4b91c2081aa7
- https://github.com/FriendsOfPHP/security-advisories/blob/master/scheb/two-factor-bundle/2018-07-08.yaml
- https://github.com/scheb/two-factor-bundle
