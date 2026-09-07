# [H] SQL injection in prestashop/prestashop

## Summary
Severity: High
Advisory: GHSA-6xxj-gcjq-wgf4
CVE: CVE-2021-43789
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-07
Source: https://github.com/advisories/GHSA-6xxj-gcjq-wgf4
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=1.7.5.0 <1.7.8.2

## Details
### Impact
Blind SQLi using Search filters with `orderBy` and `sortOrder` parameters

### Patches
The problem is fixed in 1.7.8.2

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-6xxj-gcjq-wgf4
- https://nvd.nist.gov/vuln/detail/CVE-2021-43789
- https://github.com/PrestaShop/PrestaShop/issues/26623
- https://github.com/PrestaShop/PrestaShop/commit/6482b9ddc9dcebf7588dbfd616d2d635218408d6
- https://cwe.mitre.org/data/definitions/89.html
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/1.7.8.2
