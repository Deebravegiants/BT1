# [H] Drupal Core Cross-Site Request Forgery (CSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-m648-hpf8-qcjw
CVE: CVE-2020-13663
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m648-hpf8-qcjw
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.9.0 <8.9.1
- Packagist: `drupal/core` — affected >=9.0.0 <9.0.1
- Packagist: `drupal/core` — affected >=7.0.0 <7.72
- Packagist: `drupal/core` — affected >=8.0.0 <8.8.8
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.72
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.8.8
- Packagist: `drupal/drupal` — affected >=8.9.0 <8.9.1
- Packagist: `drupal/drupal` — affected >=9.0.0 <9.0.1

## Details
Cross Site Request Forgery vulnerability in Drupal Core Form API does not properly handle certain form input from cross-site requests, which can lead to other vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13663
- https://github.com/drupal/core/commit/5f3c4d80fd77df0cfa87722b446db54040d55693
- https://github.com/drupal/core/commit/bc3235dcb5570bbda62ef9547e7604ee060b72c6
- https://github.com/drupal/core/commit/faf3243c4ce03bbaab386af2b272b363fd0dfddb
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2020-13663.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2020-13663.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2020-004
