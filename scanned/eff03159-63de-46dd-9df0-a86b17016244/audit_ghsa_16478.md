# [M] Drupal Content moderation Access bypass

## Summary
Severity: Medium
Advisory: GHSA-f84q-mgj9-8jfc
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-f84q-mgj9-8jfc
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.5.8
- Packagist: `drupal/core` — affected >=8.6.0 <8.6.2

## Details
In some conditions, drupal content moderation fails to check a users access to use certain transitions, leading to an access bypass.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/2018-10-17-1.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2018-006
