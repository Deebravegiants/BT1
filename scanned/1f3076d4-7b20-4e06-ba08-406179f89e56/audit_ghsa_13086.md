# [M] PrestaShop boolean SQL injection

## Summary
Severity: Medium
Advisory: GHSA-75p5-jwx4-qw9h
CVE: CVE-2023-39524
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-75p5-jwx4-qw9h
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.1.1

## Details
### Impact
SQL injection possible in product search field, in BO's product page

### Patches
8.1.1

### Found by
Aleksey Solovev (Positive Technologies)

### Workarounds
none

### References
none

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-75p5-jwx4-qw9h
- https://nvd.nist.gov/vuln/detail/CVE-2023-39524
- https://github.com/PrestaShop/PrestaShop/commit/2047d4c053043102bc46a37d383b392704bf14d7
- https://github.com/PrestaShop/PrestaShop
