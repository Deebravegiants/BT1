# [C] PrestaShop eval injection possible if shop vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-hrgx-p36p-89q4
CVE: CVE-2022-31181
CWE: CWE-89, CWE-95
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-hrgx-p36p-89q4
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=1.6.0.10 <1.7.8.7

## Details
### Impact
Eval injection possible if the shop is vulnerable to an SQL injection.

### Patches
The problem is fixed in version 1.7.8.7

### Workarounds
Delete the MySQL Smarty cache feature by removing these lines in the file `config/smarty.config.inc.php` lines 43-46 (PrestaShop 1.7) or 40-43 (PrestaShop 1.6):
```php
if (Configuration::get('PS_SMARTY_CACHING_TYPE') == 'mysql') {
    include _PS_CLASS_DIR_.'Smarty/SmartyCacheResourceMysql.php';
    $smarty->caching_type = 'mysql';
}
```

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-hrgx-p36p-89q4
- https://nvd.nist.gov/vuln/detail/CVE-2022-31181
- https://github.com/PrestaShop/PrestaShop/commit/b6d96e7c2a4e35a44e96ffbcdfd34439b56af804
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/1.7.8.7
