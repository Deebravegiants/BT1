# [C] Symfony XML decoding attack vector through external entities

## Summary
Severity: Critical
Advisory: GHSA-mmcv-fvq8-r9x3
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-mmcv-fvq8-r9x3
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.11

## Details
The XMLEncoder component of Symfony 2.0.x fails to disable external entities when parsing XML. In the Symfony2 framework the XML class may be used to deserialize objects or as part of a client/server API. By using external entities it is possible to include arbitrary files from the file system.

## References
- https://github.com/symfony/symfony/commit/3e64d36cbdc34acaa82e0e6318112cd2eacb6fec
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/2012-02-24.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-release-symfony-2-0-11-released
