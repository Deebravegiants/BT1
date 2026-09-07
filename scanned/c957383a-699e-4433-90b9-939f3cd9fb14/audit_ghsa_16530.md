# [M] Silverstripe Missing CSRF protection in login form

## Summary
Severity: Medium
Advisory: GHSA-vj2j-6g3w-4662
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-vj2j-6g3w-4662
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.18 <3.1.19
- Packagist: `silverstripe/framework` — affected >=3.2.3 <3.2.4
- Packagist: `silverstripe/framework` — affected >=3.3.1 <3.3.2

## Details
LoginForm calls disableSecurityToken(), which causes a "shared host domain" vulnerability: http://stackoverflow.com/a/15350123.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/a6bd22ab2f3b11a054d20be13306a19089510989
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-006-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://stackoverflow.com/questions/6412813/do-login-forms-need-tokens-against-csrf-attacks/15350123#15350123
- https://www.silverstripe.org/download/security-releases/ss-2016-006
