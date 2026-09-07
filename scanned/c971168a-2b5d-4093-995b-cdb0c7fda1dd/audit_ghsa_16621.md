# [M] Silverstripe framework is vulnerable to XSS in install.php

## Summary
Severity: Medium
Advisory: GHSA-mqf5-275h-gf6r
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-mqf5-275h-gf6r
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.14

## Details
During installation, certain parameters (admin_username and admin_password) are not escaped in the setup form.

This issue is resolved in 3.1.14 stable, although existing users are advised to remove this file prior to deploying to a production server.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/4c73721bab0d543eee6137e3c00aa8ec727e95d1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-016-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-016
