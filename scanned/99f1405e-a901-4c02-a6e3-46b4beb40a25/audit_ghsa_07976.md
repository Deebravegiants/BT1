# [M] PrestaShop affected by time based enumeration in FO login form

## Summary
Severity: Medium
Advisory: GHSA-67v7-3g49-mxh2
CVE: CVE-2026-25597
CWE: CWE-208
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-67v7-3g49-mxh2
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=9.0.0-alpha.1 <9.0.3
- Packagist: `prestashop/prestashop` — affected >=0 <8.2.4

## Details
### Impact
A time-based user enumeration vulnerability in the user authentication functionality of PrestaShop. This vulnerability allows an attacker to determine whether a customer account exists in the system by measuring response times.

### Patches
8.2.4 and 9.0.3

### Workarounds
none

### References
Found by Lam Yiu Tung

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-67v7-3g49-mxh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25597
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.2.4
- https://github.com/PrestaShop/PrestaShop/releases/tag/9.0.3
