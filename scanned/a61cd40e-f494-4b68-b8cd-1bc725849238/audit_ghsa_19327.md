# [H] OXID eShop May Display User Information

## Summary
Severity: High
Advisory: GHSA-qqcr-9jfc-35c4
CVE: CVE-2024-56526
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-qqcr-9jfc-35c4
Type: github-advisory

## Affected
- Packagist: `oxid-esales/oxideshop-ce` — affected >=6.0.0 <6.14.4
- Packagist: `oxid-esales/oxideshop-metapackage-ce` — affected >=6.0.0 <6.5.5
- Packagist: `oxid-esales/smarty-component` — affected >=0 <1.0.1

## Details
An issue was discovered in OXID eShop before 7. CMS pages in combination with Smarty may display user information if a CMS page contains a Smarty syntax error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56526
- https://bugs.oxid-esales.com/view.php?id=7743
- https://github.com/OXID-eSales/oxideshop_ce
- https://github.com/OXID-eSales/oxideshop_ce/releases/tag/v6.14.4
- https://github.com/OXID-eSales/oxideshop_metapackage_ce/releases/tag/v6.5.5
