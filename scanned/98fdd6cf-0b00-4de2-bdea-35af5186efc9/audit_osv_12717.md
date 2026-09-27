# [H] CVE-2018-14472

## Summary
Severity: High
Advisory: CVE-2018-14472
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-20
Source: https://osv.dev/vulnerability/CVE-2018-14472
Type: osv

## Details
An issue was discovered in WUZHI CMS 4.1.0. The vulnerable file is coreframe/app/order/admin/goods.php. The $keywords parameter is taken directly into execution without any filtering, leading to SQL injection.

## References
- https://github.com/wuzhicms/wuzhicms/issues/144
