# [H] Drupal core access bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-3xr3-phjp-g6p2
CVE: CVE-2020-13677
CWE: CWE-284, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-3xr3-phjp-g6p2
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=8.0.0 <8.9.19
- Packagist: `drupal/core` — affected >=9.1.0 <9.1.13
- Packagist: `drupal/core` — affected >=9.2.0 <9.2.6

## Details
Under some circumstances, the Drupal core JSON:API module does not properly restrict access to certain content, which may result in unintended access bypass. Sites that do not have the JSON:API module enabled are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13677
- https://github.com/drupal/core/commit/7a9bef4b4750d79ab42498e459012cabe4c4bd8b
- https://github.com/drupal/core
- https://www.drupal.org/sa-core-2021-010
