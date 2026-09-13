# [H] easyadmin-extension-bundle action case insensitivity

## Summary
Severity: High
Advisory: GHSA-32rx-xvvr-4xv9
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-32rx-xvvr-4xv9
Type: github-advisory

## Affected
- Packagist: `alterphp/easyadmin-extension-bundle` — affected >=1.3.0 <1.3.1
- Packagist: `alterphp/easyadmin-extension-bundle` — affected >=1.2.0 <1.2.11

## Details
In alterphp/easyadmin-extension-bundle, role based access rules do not handle action name case sensitivity which may lead to unauthorized access.

## References
- https://github.com/alterphp/EasyAdminExtensionBundle/commit/68407ca5be644d1c53fb894453df951230afc6dc
- https://github.com/FriendsOfPHP/security-advisories/blob/master/alterphp/easyadmin-extension-bundle/2018-10-02.yaml
- https://github.com/alterphp/EasyAdminExtensionBundle/releases/tag/v1.3.1
