# [M] Symfony may allow a user to switch to using another user's identity

## Summary
Severity: Medium
Advisory: GHSA-7mx2-7q8p-pgmw
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-7mx2-7q8p-pgmw
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.6

## Details
Symfony 2.0.6 has just been released. It addresses a security vulnerability in the EntityUserProvider as provided in the Doctrine bridge.

If you let your users update their login/username from a form, and if you are using Doctrine as a user provider, then you are vulnerable and you should upgrade as soon as possible.

The issue is that it is possible for a user to switch to another one. Here is how to reproduce it: The current user changes its username via a form to another existing username. When the form is submitted, he will have a validation error (as the username already exists) but the user object in the session will still be modified to the new username. This user from the session will be used for the next requests and so the user will be switched to this other user.

The fix is to always refresh the user via the primary key (which cannot be updated via a form) instead of the username.

If you cannot upgrade immediately, please apply the following patch: https://github.com/symfony/symfony/commit/9d2ab9ca9c1762

## References
- https://github.com/symfony/symfony/commit/9d2ab9ca9c1762
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/2011-11-16.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-release-symfony-2-0-6
