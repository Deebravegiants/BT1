# [H] Drupal core Denial of Service

## Summary
Severity: High
Advisory: GHSA-xq54-x54m-vcpx
CVE: CVE-2024-11941
CWE: CWE-835
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-xq54-x54m-vcpx
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=10.1.0 <10.1.8
- Packagist: `drupal/core` — affected >=10.2.0 <10.2.2

## Details
The Comment module allows users to reply to comments. In certain cases, an attacker could make comment reply requests that would trigger a denial of service (DOS).

Sites that do not use the Comment module are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11941
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2024-001
