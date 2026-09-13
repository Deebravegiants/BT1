# [H] FOSUserBundle Session Hijacking Vulnerability

## Summary
Severity: High
Advisory: GHSA-6mjq-9x4w-m3w9
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-6mjq-9x4w-m3w9
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony/user-bundle` — affected >=1.2.0 <1.2.4

## Details
Versions of FOSUserBundle from 1.2.x to 1.2.4 have been found to contain a security vulnerability related to session hijacking. This issue has been addressed in version 1.2.4, and users are strongly advised to upgrade to the latest version to prevent potential session-related security risks.

## References
- https://github.com/FriendsOfSymfony/FOSUserBundle/commit/8e412a70cafd924ad04c7325dae423048861b955
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony/user-bundle/2012-07-10-2.yaml
- https://github.com/FriendsOfSymfony/FOSUserBundle
- https://github.com/FriendsOfSymfony/FOSUserBundle/blob/master/Changelog.md
