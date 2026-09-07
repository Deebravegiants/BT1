# [M] Drupal External URL injection through URL aliases leading to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-7f4f-p7mq-p4fv
CWE: CWE-601
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-7f4f-p7mq-p4fv
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.60
- Packagist: `drupal/core` — affected >=8.0.0 <8.5.8
- Packagist: `drupal/core` — affected >=8.6.0 <8.6.2

## Details
The path module in Drupal allows users with the 'administer paths' to create pretty URLs for content.
In certain circumstances the user can enter a particular path that triggers an open redirect to a malicious url.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/2018-10-17-2.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2018-006
