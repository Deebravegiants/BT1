# [C] PrestaShop SQL manager vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gf46-prm4-56pc
CVE: CVE-2023-39526
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-gf46-prm4-56pc
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.1.0 <8.1.1
- Packagist: `prestashop/prestashop` — affected >=8.0.0 <8.0.5
- Packagist: `prestashop/prestashop` — affected >=0 <1.7.8.10

## Details
### Impact
Remote code execution through SQL injection and arbitrary file write in back office

### Patches
1.7.8.10
8.0.5
8.1.1

### Found by
Truff (via yeswehack)

### Workarounds
none

### References
none

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-gf46-prm4-56pc
- https://nvd.nist.gov/vuln/detail/CVE-2023-39526
- https://github.com/PrestaShop/PrestaShop/commit/817847e2347844a9b6add017581f1932bcd28c09
- https://github.com/PrestaShop/PrestaShop
