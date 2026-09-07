# [H] WooCommerce Cross-Site Request Forgery (CSRF) 

## Summary
Severity: High
Advisory: GHSA-rcmf-88p4-9wrg
CVE: CVE-2019-20891
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rcmf-88p4-9wrg
Type: github-advisory

## Affected
- Packagist: `woocommerce/woocommerce` — affected >=0 <3.6.5

## Details
WooCommerce before 3.6.5, when it handles CSV imports of products, has a cross-site request forgery (CSRF) issue with resultant stored cross-site scripting (XSS) via `includes/admin/importers/class-wc-product-csv-importer-controller.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20891
- https://github.com/woocommerce/woocommerce/commit/fd7feb778eb45a2eb92b45eb2b4ee96ea3ac6fe7
- https://blog.ripstech.com/2019/woocommerce-csrf-to-stored-xss
- https://github.com/woocommerce/woocommerce
- https://raw.githubusercontent.com/woocommerce/woocommerce/master/CHANGELOG.txt
