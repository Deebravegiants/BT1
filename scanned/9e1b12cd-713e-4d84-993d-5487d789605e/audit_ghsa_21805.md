# [M] Cross-Site Request Forgery in Drupal core

## Summary
Severity: Medium
Advisory: GHSA-j586-cj67-vg4p
CVE: CVE-2020-13674
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-j586-cj67-vg4p
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.9.19
- Packagist: `drupal/core` — affected >=9.1.0 <9.1.13
- Packagist: `drupal/core` — affected >=9.2.0 <9.2.6

## Details
The QuickEdit module does not properly validate access to routes, which could allow cross-site request forgery under some circumstances and lead to possible data integrity issues. Sites are only affected if the QuickEdit module (which comes with the Standard profile) is installed. Removing the "access in-place editing" permission from untrusted users will not fully mitigate the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13674
- https://github.com/drupal/core/commit/20cd85db8198c63101bd050ea973b13f2f3edef6
- https://github.com/drupal/core/commit/6359b3ea5aacf85399285c522c6d787a218c897c
- https://github.com/drupal/core/commit/801910fcdfc14ee6120051089a2129e455186ad8
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2021-007
