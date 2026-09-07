# [M] Cross-site Scripting in Drupal Core

## Summary
Severity: Medium
Advisory: GHSA-m6q5-wv4x-fv6h
CVE: CVE-2020-13668
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-m6q5-wv4x-fv6h
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.8.10
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.6
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.6
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.8.10
- Packagist: `drupal/drupal` — affected >=8.9.0 <8.9.6
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.6

## Details
Access Bypass vulnerability in Drupal Core allows for an attacker to leverage the way that HTML is rendered for affected forms in order to exploit the vulnerability. This issue affects: Drupal Core 8.8.x versions prior to 8.8.10; 8.9.x versions prior to 8.9.6; 9.0.x versions prior to 9.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13668
- https://github.com/drupal/core/commit/3184fa4b2f3b65b44884b5e858cdc7794d34b4c8
- https://github.com/drupal/core/commit/58330ba58d1ac6f1a0a549e8dbde8a3e094bf4fb
- https://github.com/drupal/core/commit/d4be028d81fb6b067513d788b60c3e6fc8fbd0a2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13668.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13668.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2020-009
