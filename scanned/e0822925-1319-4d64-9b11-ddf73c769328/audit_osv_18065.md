# [C] CVE-2020-23360

## Summary
Severity: Critical
Advisory: CVE-2020-23360
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2020-23360
Type: osv

## Details
oscommerce v2.3.4.1 has a functional problem in user registration and password rechecking, where a non-identical password can bypass the checks in /catalog/admin/administrators.php and /catalog/password_reset.php

## References
- https://github.com/osCommerce/oscommerce2/issues/658
