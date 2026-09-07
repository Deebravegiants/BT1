# [M] Drupal Settings Tray access bypass

## Summary
Severity: Medium
Advisory: GHSA-7ffh-cjvg-fpr4
CVE: CVE-2017-6931
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7ffh-cjvg-fpr4
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.4.0 <8.4.5
- Packagist: `drupal/drupal` — affected >=8.4.0 <8.4.5

## Details
In Drupal versions 8.4.x versions before 8.4.5 the Settings Tray module has a vulnerability that allows users to update certain data that they do not have the permissions for. If you have implemented a Settings Tray form in contrib or a custom module, the correct access checks should be added. This release fixes the only two implementations in core, but does not harden against other such bypasses. This vulnerability can be mitigated by disabling the Settings Tray module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6931
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/core/CVE-2017-6931.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/drupal/drupal/CVE-2017-6931.yaml
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2018-001
