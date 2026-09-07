# [H] Drupal REST API can bypass comment approval

## Summary
Severity: High
Advisory: GHSA-p8g6-5mg7-9r5q
CVE: CVE-2017-6924
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p8g6-5mg7-9r5q
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.3.7
- Packagist: `drupal/drupal` — affected >=8.0 <8.3.7

## Details
In Drupal 8 prior to 8.3.7; When using the REST API, users without the correct permission can post comments via REST that are approved even if the user does not have permission to post approved comments. This issue only affects sites that have the RESTful Web Services (rest) module enabled, the comment entity REST resource enabled, and where an attacker can access a user account on the site with permissions to post comments, or where anonymous users can post comments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6924
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6924.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6924.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2017-004
- https://www.drupal.org/forum/newsletters/security-advisories-for-drupal-core/2017-08-16/drupal-core-multiple
- http://www.securityfocus.com/bid/100368
- http://www.securitytracker.com/id/1039200
