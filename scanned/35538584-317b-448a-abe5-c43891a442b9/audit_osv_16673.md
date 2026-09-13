# [C] CVE-2019-9025

## Summary
Severity: Critical
Advisory: CVE-2019-9025
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-22
Source: https://osv.dev/vulnerability/CVE-2019-9025
Type: osv

## Details
An issue was discovered in PHP 7.3.x before 7.3.1. An invalid multibyte string supplied as an argument to the mb_split() function in ext/mbstring/php_mbregex.c can cause PHP to execute memcpy() with a negative argument, which could read and write past buffers allocated for the data.

## References
- https://security.netapp.com/advisory/ntap-20190321-0001/
- https://bugs.php.net/bug.php?id=77367
