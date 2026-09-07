# [M] Backdrop CMS does not sufficiently sanitize field labels before they are displayed in certain places

## Summary
Severity: Medium
Advisory: GHSA-3wmx-48g3-x66g
CVE: CVE-2024-41709
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-3wmx-48g3-x66g
Type: github-advisory

## Affected
- Packagist: `backdrop/backdrop` — affected >=0 <1.27.3
- Packagist: `backdrop/backdrop` — affected >=1.28.0 <1.28.2

## Details
Backdrop CMS before 1.27.3 and 1.28.x before 1.28.2 does not sufficiently sanitize field labels before they are displayed in certain places. This vulnerability is mitigated by the fact that an attacker must have a role with the "administer fields" permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41709
- https://github.com/backdrop/backdrop/commit/c7ff0500705668e3f58263590812872e44059301
- https://github.com/backdrop/backdrop/commit/f1dfe710c186fb47c9d949f01f37e5ab42b44030
- https://backdropcms.org/security/backdrop-sa-core-2024-001
- https://github.com/backdrop-ops/backdrop-composer
