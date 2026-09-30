# [M] Sylius Admin Bundle Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-945h-6vcv-pc8h
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-945h-6vcv-pc8h
Type: github-advisory

## Affected
- Packagist: `sylius/admin-bundle` — affected >=1.0.0 <1.0.17
- Packagist: `sylius/admin-bundle` — affected >=1.1.0 <1.1.9
- Packagist: `sylius/admin-bundle` — affected >=1.2.0 <1.2.2

## Details
Sylius 1.0.0 to 1.0.16, 1.1.0 to 1.1.8, 1.2.0 to 1.2.1 versions of AdminBundle and ResourceBundle are affected by this security issue.

This issue has been fixed in Sylius 1.0.17, 1.1.9 and 1.2.2. Development branch for 1.3 release has also been fixed.

### Description

The following actions in the admin panel did not require a CSRF token:

- marking order’s payment as completed
- marking order’s payment as refunded
- marking product review as accepted
- marking product review as rejected

### Resolution

The issue is fixed by adding a required CSRF token to those actions.

We also fixed `ResourceController`‘s  `applyStateMachineTransitionAction` method by adding a CSRF token check. If you use that action in the API context, you can disable it by adding `csrf_protection:` false to its routing configuration

## References
- https://github.com/Sylius/SyliusAdminBundle/commit/79c2d963bed61411b1eef15715a74d2d96b91884
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/admin-bundle/2018-07-09.yaml
- https://github.com/Sylius/SyliusAdminBundle
- https://sylius.com/blog/csrf-vulnerability-in-admin-panel
