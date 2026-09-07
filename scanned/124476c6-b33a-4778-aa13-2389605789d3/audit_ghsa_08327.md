# [M] Drupal core is Vulnerable to Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-f3cj-mjqm-fhvj
CVE: CVE-2026-6365
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-f3cj-mjqm-fhvj
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <10.5.9
- Packagist: `drupal/core` — affected >=10.6.0 <10.6.7
- Packagist: `drupal/core` — affected >=11.0.0 <11.2.11
- Packagist: `drupal/core` — affected >=11.3.0 <11.3.7

## Details
Improper Neutralization of Input During Web Page Generation ("Cross-site Scripting") vulnerability in Drupal Drupal core allows Cross-Site Scripting (XSS).

This issue affects Drupal core: from 8.0.0 before 10.5.9, from 10.6.0 before 10.6.7, from 11.0.0 before 11.2.11, from 11.3.0 before 11.3.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6365
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2026-001
