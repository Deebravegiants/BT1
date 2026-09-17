# [H] scheb/two-factor-bundle bypass two-factor authentication with remember-me option

## Summary
Severity: High
Advisory: GHSA-9phw-7h96-q3rv
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-9phw-7h96-q3rv
Type: github-advisory

## Affected
- Packagist: `scheb/two-factor-bundle` — affected >=4.0.0 <4.11.0
- Packagist: `scheb/two-factor-bundle` — affected >=0 <3.26.0

## Details
In versions prior to 3.26.0 and prior to 4.11.0 of the "scheb/two-factor-bundle" project, a security vulnerability allowed attackers to bypass two-factor authentication (2FA) using the remember_me cookie. When the remember_me checkbox was used during login, a "REMEMBERME" cookie was created. Upon redirection to the 2FA page, attackers could manipulate the SESSIONID key, granting access to the homepage "/" and gaining authentication without completing 2FA.

## References
- https://github.com/scheb/two-factor-bundle/issues/253
- https://github.com/scheb/two-factor-bundle/commit/3fbca9e821985559b444207a7c2d73b9b569b58b
- https://github.com/scheb/two-factor-bundle/commit/a149808d25c1553757c529b9568913ea1cec0894
- https://github.com/FriendsOfPHP/security-advisories/blob/master/scheb/two-factor-bundle/2019-12-19.yaml
- https://github.com/scheb/two-factor-bundle
