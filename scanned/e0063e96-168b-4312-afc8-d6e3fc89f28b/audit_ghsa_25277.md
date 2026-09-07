# [C] Drupal PECL YAML parser unsafe object handling

## Summary
Severity: Critical
Advisory: GHSA-9c24-g32g-35rj
CVE: CVE-2017-6920
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9c24-g32g-35rj
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.3.4
- Packagist: `drupal/drupal` — affected >=8.0 <8.3.4

## Details
Drupal core 8 before versions 8.3.4 allows remote attackers to execute arbitrary code due to the PECL YAML parser not handling PHP objects safely during certain operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6920
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6920.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6920.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-CORE-2017-003
- https://www.drupal.org/forum/newsletters/security-advisories-for-drupal-core/2017-06-21/drupal-core-multiple
- http://www.securityfocus.com/bid/99211
- http://www.securitytracker.com/id/1038781
