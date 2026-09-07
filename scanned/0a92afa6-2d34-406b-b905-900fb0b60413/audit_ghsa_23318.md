# [M] Drupal file REST resource does not properly validate

## Summary
Severity: Medium
Advisory: GHSA-h377-287m-w2r9
CVE: CVE-2017-6921
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h377-287m-w2r9
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.3.4
- Packagist: `drupal/drupal` — affected >=8.0 <8.3.4

## Details
In Drupal 8 prior to 8.3.4; The file REST resource does not properly validate some fields when manipulating files. A site is only affected by this if the site has the RESTful Web Services (rest) module enabled, the file REST resource is enabled and allows PATCH requests, and an attacker can get or register a user account on the site with permissions to upload files and to modify the file resource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6921
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6921.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6921.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2017-003
- https://www.drupal.org/forum/newsletters/security-advisories-for-drupal-core/2017-06-21/drupal-core-multiple
- http://www.securityfocus.com/bid/99222
- http://www.securitytracker.com/id/1038781
