# [M] Drupal Users without "Administer comments" can set comment visibility on nodes they can edit

## Summary
Severity: Medium
Advisory: GHSA-6g9h-6v79-w4pc
CVE: CVE-2016-7570
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6g9h-6v79-w4pc
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.1.10
- Packagist: `drupal/core` — affected >=8.0.0 <8.1.10

## Details
Drupal 8.x before 8.1.10 does not properly check for "Administer comments" permission, which allows remote authenticated users to set the visibility of comments for arbitrary nodes by leveraging rights to edit those nodes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7570
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2016-7570.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2016-7570.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2016-004
- http://www.securityfocus.com/bid/93101
- http://www.securitytracker.com/id/1036886
