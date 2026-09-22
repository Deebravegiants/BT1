# [H] CVE-2016-10159

## Summary
Severity: High
Advisory: CVE-2016-10159
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-24
Source: https://osv.dev/vulnerability/CVE-2016-10159
Type: osv

## Details
Integer overflow in the phar_parse_pharfile function in ext/phar/phar.c in PHP before 5.6.30 and 7.0.x before 7.0.15 allows remote attackers to cause a denial of service (memory consumption or application crash) via a truncated manifest entry in a PHAR archive.

## References
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.debian.org/security/2017/dsa-3783
- http://www.securityfocus.com/bid/95774
- http://www.securitytracker.com/id/1037659
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201702-29
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.tenable.com/security/tns-2017-04
- https://bugs.php.net/bug.php?id=73764
- https://github.com/php/php-src/commit/ca46d0acbce55019b970fcd4c1e8a10edfdded93
