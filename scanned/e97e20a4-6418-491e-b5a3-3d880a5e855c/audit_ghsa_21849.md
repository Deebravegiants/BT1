# [M] Incorrect Authorization in Drupal core

## Summary
Severity: Medium
Advisory: GHSA-qfhg-m6r8-xxpj
CVE: CVE-2020-13676
CWE: CWE-284, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-qfhg-m6r8-xxpj
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.9.19
- Packagist: `drupal/core` — affected >=9.1.0 <9.1.13
- Packagist: `drupal/core` — affected >=9.2.0 <9.2.6

## Details
The QuickEdit module does not properly check access to fields in some circumstances, which can lead to unintended disclosure of field data. Sites are only affected if the QuickEdit module (which comes with the Standard profile) is installed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13676
- https://github.com/drupal/core/commit/8e8e3d2ddd72471ba886346ecabfb5d98fd27d9b
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2021-009
