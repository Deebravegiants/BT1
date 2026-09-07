# [H] Drupal core contains a potential PHP Object Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-gvf2-2f4g-jqf4
CVE: CVE-2024-55638
CWE: CWE-502, CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-10
Source: https://github.com/advisories/GHSA-gvf2-2f4g-jqf4
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.8.0 <10.2.11
- Packagist: `drupal/core` — affected >=10.3.0 <10.3.9
- Packagist: `drupal/core` — affected >=7.0 <7.102
- Packagist: `drupal/core-recommended` — affected >=8.8.0 <10.2.11
- Packagist: `drupal/core-recommended` — affected >=10.3.0 <10.3.9
- Packagist: `drupal/core-recommended` — affected >=7.0 <7.102
- Packagist: `drupal/drupal` — affected >=8.8.0 <10.2.11
- Packagist: `drupal/drupal` — affected >=10.3.0 <10.3.9
- Packagist: `drupal/drupal` — affected >=7.0 <7.102

## Details
Drupal core contains a potential PHP Object Injection vulnerability that (if combined with another exploit) could lead to Remote Code Execution. It is not directly exploitable.

This issue is mitigated by the fact that in order for it to be exploitable, a separate vulnerability must be present to allow an attacker to pass unsafe input to `unserialize()`. There are no such known exploits in Drupal core.

To help protect against this potential vulnerability, some additional checks have been added to Drupal core's database code. If you use a third-party database driver, check the release notes for additional configuration steps that may be required in certain cases. 

This issue affects Drupal Core: from 7.0 before 7.102, from 8.0.0 before 10.2.11, from 10.3.0 before 10.3.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55638
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2024-008
