# [H] CVE-2018-18573

## Summary
Severity: High
Advisory: CVE-2018-18573
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-22
Source: https://osv.dev/vulnerability/CVE-2018-18573
Type: osv

## Details
osCommerce 2.3.4.1 has an incomplete '.htaccess' for blacklist filtering in the "product" page. Remote authenticated administrators can upload new '.htaccess' files (e.g., omitting .php) and subsequently achieve arbitrary PHP code execution via a /catalog/admin/categories.php?cPath=&action=new_product URI.

## References
- https://github.com/osCommerce/oscommerce2/issues/631
