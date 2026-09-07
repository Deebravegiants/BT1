# [H] Drupal Open Social Missing Authorization vulnerability

## Summary
Severity: High
Advisory: GHSA-m9w8-wxvp-c9gv
CVE: CVE-2025-31686
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-m9w8-wxvp-c9gv
Type: github-advisory

## Affected
- Packagist: `goalgorilla/open_social` — affected >=0 <12.3.11
- Packagist: `goalgorilla/open_social` — affected >=12.4.0 <12.4.10

## Details
Missing Authorization vulnerability in Drupal Open Social allows Forceful Browsing. This issue affects Open Social: from 0.0.0 before 12.3.11, from 12.4.0 before 12.4.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31686
- https://github.com/goalgorilla/open_social/commit/6830b1788616fc24fb3913ce88c5d997a363a5de
- https://github.com/goalgorilla/open_social/commit/6fa5181901d4be3a64793f29c6ce0c9bd535a42f
- https://github.com/goalgorilla/open_social
- https://www.drupal.org/sa-contrib-2025-015
