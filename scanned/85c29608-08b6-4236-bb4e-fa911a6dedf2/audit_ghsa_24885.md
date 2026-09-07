# [M] Reflected XSS in Zen Cart before 1.5.7a

## Summary
Severity: Medium
Advisory: GHSA-wxxx-2x6v-979f
CVE: CVE-2020-6578
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wxxx-2x6v-979f
Type: github-advisory

## Affected
- Packagist: `zencart/zencart` — affected >=0 <1.5.7a

## Details
Zen Cart 1.5.6d allows reflected XSS via the main_page parameter to `includes/templates/template_default/common/tpl_main_page.php` or `includes/templates/responsive_classic/common/tpl_main_page.php.`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-6578
- https://github.com/zencart/zencart/commit/aa11e1e06c11b8a2940299a4bec0ac3dd95a7895
- https://herolab.usd.de/security-advisories/usd-2019-0069
