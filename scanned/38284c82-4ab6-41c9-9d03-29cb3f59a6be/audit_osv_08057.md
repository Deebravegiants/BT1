# [H] CVE-2016-10158

## Summary
Severity: High
Advisory: CVE-2016-10158
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-24
Source: https://osv.dev/vulnerability/CVE-2016-10158
Type: osv

## Details
The exif_convert_any_to_int function in ext/exif/exif.c in PHP before 5.6.30, 7.0.x before 7.0.15, and 7.1.x before 7.1.1 allows remote attackers to cause a denial of service (application crash) via crafted EXIF data that triggers an attempt to divide the minimum representable negative integer by -1.

## References
- http://www.securitytracker.com/id/1037659
- https://www.tenable.com/security/tns-2017-04
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.debian.org/security/2017/dsa-3783
- http://www.securityfocus.com/bid/95764
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201702-29
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=73737
- https://github.com/php/php-src/commit/1cda0d7c2ffb62d8331c64e703131d9cabdc03ea
