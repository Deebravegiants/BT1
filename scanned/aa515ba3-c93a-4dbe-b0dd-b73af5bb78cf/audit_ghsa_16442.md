# [M]  Drupal core Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wxfg-253g-m7r4
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-wxfg-253g-m7r4
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.70

## Details
Drupal 7 has an Open Redirect vulnerability. For example, a user could be tricked into visiting a specially crafted link which would redirect them to an arbitrary external URL.

The vulnerability is caused by insufficient validation of the destination query parameter in the drupal_goto() function.

Other versions of Drupal core are not vulnerable.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/2020-05-20-1.yaml
- https://github.com/drupal/drupal
- https://www.drupal.org/sa-core-2020-003
