# [H] Improper input validation in Drupal core

## Summary
Severity: High
Advisory: GHSA-g36h-4jr6-qmm9
CVE: CVE-2022-25273
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-g36h-4jr6-qmm9
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <9.2.18
- Packagist: `drupal/core` — affected >=9.3.0 <9.3.12

## Details
Drupal core's form API has a vulnerability where certain contributed or custom modules' forms may be vulnerable to improper input validation. This could allow an attacker to inject disallowed values or overwrite data. Affected forms are uncommon, but in certain cases an attacker could alter critical or sensitive data.

Drupal 7 is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25273
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2022-008
