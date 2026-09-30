# [M] doctrine/doctrine-module zero-valued authentication credentials vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9wv8-3h8h-x2wc
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-9wv8-3h8h-x2wc
Type: github-advisory

## Affected
- Packagist: `doctrine/doctrine-module` — affected >=0 <0.7.2

## Details
it is possible (under certain circumstances) to obtain a valid `Zend\Authentication` identity even without knowing the user's credentials by using a numerically valued credential in `DoctrineModule\Authentication\Adapter\ObjectRepository`.

## References
- https://github.com/doctrine/DoctrineModule/issues/248
- https://github.com/doctrine/DoctrineModule/issues/249
- https://github.com/doctrine/DoctrineModule/commit/78018ef568c52e65a0b17e7bd5a4c90fe6673e84
- https://github.com/FriendsOfPHP/security-advisories/blob/master/doctrine/doctrine-module/2013-05-16.yaml
- https://github.com/doctrine/DoctrineModule
