# [M] FOSUserBundle User Identity Validation Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8wx3-8m4x-g5h4
CWE: CWE-285
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-8wx3-8m4x-g5h4
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony/user-bundle` — affected >=1.0.0 <1.2.1

## Details
Versions of FOSUserBundle prior to 1.2.1 have been found to be vulnerable to a security issue related to user identity validation. Specifically, user refreshing was performed using the primary key instead of the username, leading to a potential security risk if a user is allowed to change their username. The fix in version 1.2.1 addresses this issue by loading the user using the primary key during refreshing.

## References
- https://github.com/FriendsOfSymfony/FOSUserBundle/commit/1b8bc18e3d99ef0b52b4141f20da323033d6be9b
- https://github.com/FriendsOfSymfony/FOSUserBundle/commit/5a36e2958068d1e6501dc8cf39bbae3ebb859d9f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony/user-bundle/2012-07-10-1.yaml
- https://github.com/FriendsOfSymfony/FOSUserBundle
- https://github.com/FriendsOfSymfony/FOSUserBundle/blob/master/Changelog.md
