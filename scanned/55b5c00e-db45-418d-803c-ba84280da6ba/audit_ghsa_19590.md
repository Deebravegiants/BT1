# [M] Drupal Core Potential Cross-Site Scripting (XSS) via Error Messages

## Summary
Severity: Medium
Advisory: GHSA-39g6-x4x8-5jcm
CVE: CVE-2025-3057
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-39g6-x4x8-5jcm
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <10.3.13
- Packagist: `drupal/core` — affected >=10.4.0 <10.4.3
- Packagist: `drupal/core` — affected >=11.0.0 <11.0.12
- Packagist: `drupal/core` — affected >=11.1.0 <11.1.3

## Details
Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Drupal Drupal core allows Cross-Site Scripting (XSS).This issue affects Drupal core: from 8.0.0 before 10.3.13, from 10.4.0 before 10.4.3, from 11.0.0 before 11.0.12, from 11.1.0 before 11.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3057
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2025-001
