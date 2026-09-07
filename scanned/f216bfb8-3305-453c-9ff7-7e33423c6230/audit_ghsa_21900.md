# [M] Drupal core Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3m36-mjwj-352c
CVE: CVE-2020-13672
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-3m36-mjwj-352c
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0.0 <7.80
- Packagist: `drupal/core` — affected >=8.0.0 <8.9.14
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.12
- Packagist: `drupal/core` — affected >=9.1.0 <9.1.7
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.80
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.9.14
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.12
- Packagist: `drupal/drupal` — affected >=9.1.0 <9.1.7

## Details
Cross-site Scripting (XSS) vulnerability in Drupal core's sanitization API fails to properly filter cross-site scripting under certain circumstances. This issue affects: Drupal Core 9.1.x versions prior to 9.1.7; 9.0.x versions prior to 9.0.12; 8.9.x versions prior to 8.9.14; 7.x versions prior to 7.80.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13672
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13672.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13672.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2021-002
