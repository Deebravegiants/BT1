# [M] CVE-2018-18966

## Summary
Severity: Medium
Advisory: CVE-2018-18966
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-18966
Type: osv

## Details
osCommerce 2.3.4.1 has an incomplete '.htaccess' for blacklist filtering in the "product" page. The .htaccess file in catalog/images/ bans the html extension, but Internet Explorer render HTML elements in a .eml file.

## References
- https://github.com/osCommerce/oscommerce2/issues/631
