# [H] PrestaShop XSS injection through Validate::isCleanHTML method

## Summary
Severity: High
Advisory: GHSA-xw2r-f8xv-c8xp
CVE: CVE-2023-39527
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-xw2r-f8xv-c8xp
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.1.0 <8.1.1
- Packagist: `prestashop/prestashop` — affected >=8.0.0 <8.0.5
- Packagist: `prestashop/prestashop` — affected >=0 <1.7.8.10

## Details
### Impact
xss injection through `isCleanHTML` method

### Patches
1.7.8.10
8.0.5
8.1.1

### Found by
Aleksey Solovev (Positive Technologies)

### Workarounds

### References

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-xw2r-f8xv-c8xp
- https://nvd.nist.gov/vuln/detail/CVE-2023-39527
- https://github.com/PrestaShop/PrestaShop/commit/afc14f8eaa058b3e6a20ac43e033ee2656fb88b4
- https://github.com/PrestaShop/PrestaShop
