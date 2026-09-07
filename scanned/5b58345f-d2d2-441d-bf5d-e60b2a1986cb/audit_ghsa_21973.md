# [M] Drupal core Cross-site Scripting (XSS) vulnerability in ckeditor

## Summary
Severity: Medium
Advisory: GHSA-c533-c843-67h8
CVE: CVE-2020-13669
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-c533-c843-67h8
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.8.10
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.6
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.6
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.8.10
- Packagist: `drupal/drupal` — affected >=8.9.0 <8.9.6
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.6

## Details
Cross-site Scripting (XSS) vulnerability in ckeditor of Drupal Core allows attacker to inject XSS. This issue affects: Drupal Core 8.8.x versions prior to 8.8.10.; 8.9.x versions prior to 8.9.6; 9.0.x versions prior to 9.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13669
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13669.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13669.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2020-010
