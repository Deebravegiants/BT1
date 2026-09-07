# [C] Drupal Core has a SQL Injection issue

## Summary
Severity: Critical
Advisory: GHSA-ghwc-95x2-682j
CVE: CVE-2026-9082
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-ghwc-95x2-682j
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.9.0 <10.4.10
- Packagist: `drupal/core` — affected >=10.5.0 <10.5.10
- Packagist: `drupal/core` — affected >=10.6.0 <10.6.9
- Packagist: `drupal/core` — affected >=11.0.0 <11.1.10
- Packagist: `drupal/core` — affected >=11.2.0 <11.2.12
- Packagist: `drupal/core` — affected >=11.3.0 <11.3.10

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Drupal Drupal core allows SQL Injection.

This issue affects Drupal core: from 8.9.0 before 10.4.10, from 10.5.0 before 10.5.10, from 10.6.0 before 10.6.9, from 11.0.0 before 11.1.10, from 11.2.0 before 11.2.12, from 11.3.0 before 11.3.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9082
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2026-004
