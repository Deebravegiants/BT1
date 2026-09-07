# [H] Drupal access control bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-6hpj-9xj7-2jxx
CVE: CVE-2017-6919
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6hpj-9xj7-2jxx
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0 <8.2.8
- Packagist: `drupal/core` — affected >=8.3.0 <8.3.1
- Packagist: `drupal/drupal` — affected >=8.0 <8.2.8
- Packagist: `drupal/drupal` — affected >=8.3.0 <8.3.1

## Details
Drupal 8 before 8.2.8 and 8.3 before 8.3.1 allows critical access bypass by authenticated users if the RESTful Web Services (rest) module is enabled and the site allows PATCH requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6919
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6919.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6919.yaml
- https://github.com/drupal/core
- https://www.drupal.org/SA-2017-002
- https://www.drupal.org/SA-CORE-2017-002
- http://www.securityfocus.com/bid/97941
- http://www.securitytracker.com/id/1038371
