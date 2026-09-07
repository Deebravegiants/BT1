# [C] Drupal Entity access bypass for entities that do not have UUIDs or have protected revisions

## Summary
Severity: Critical
Advisory: GHSA-f4qx-jqfq-7785
CVE: CVE-2017-6925
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-f4qx-jqfq-7785
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.3.7
- Packagist: `drupal/drupal` — affected >=8.0 <8.3.7

## Details
In versions of Drupal 8 core prior to 8.3.7; There is a vulnerability in the entity access system that could allow unwanted access to view, create, update, or delete entities. This only affects entities that do not use or do not have UUIDs, and entities that have different access restrictions on different revisions of the same entity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6925
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6925.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6925.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2017-004
- https://www.drupal.org/forum/newsletters/security-advisories-for-drupal-core/2017-08-16/drupal-core-multiple
- http://www.securityfocus.com/bid/100368
- http://www.securitytracker.com/id/1039200
