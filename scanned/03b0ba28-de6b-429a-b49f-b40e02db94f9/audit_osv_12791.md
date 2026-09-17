# [H] CVE-2018-14884

## Summary
Severity: High
Advisory: CVE-2018-14884
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-03
Source: https://osv.dev/vulnerability/CVE-2018-14884
Type: osv

## Details
An issue was discovered in PHP 7.0.x before 7.0.27, 7.1.x before 7.1.13, and 7.2.x before 7.2.1. Inappropriately parsing an HTTP response leads to a segmentation fault because http_header_value in ext/standard/http_fopen_wrapper.c can be a NULL value that is mishandled in an atoi call.

## References
- http://php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2019:2519
- https://security.netapp.com/advisory/ntap-20181107-0003/
- https://bugs.php.net/bug.php?id=75535
