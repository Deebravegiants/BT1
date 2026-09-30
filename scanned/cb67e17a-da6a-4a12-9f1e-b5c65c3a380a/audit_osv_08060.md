# [H] CVE-2016-10161

## Summary
Severity: High
Advisory: CVE-2016-10161
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-24
Source: https://osv.dev/vulnerability/CVE-2016-10161
Type: osv

## Details
The object_common1 function in ext/standard/var_unserializer.c in PHP before 5.6.30, 7.0.x before 7.0.15, and 7.1.x before 7.1.1 allows remote attackers to cause a denial of service (buffer over-read and application crash) via crafted serialized data that is mishandled in a finish_nested_data call.

## References
- http://www.securitytracker.com/id/1037659
- https://www.tenable.com/security/tns-2017-04
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.debian.org/security/2017/dsa-3783
- http://www.securityfocus.com/bid/95768
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201702-29
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=73825
- https://github.com/php/php-src/commit/16b3003ffc6393e250f069aa28a78dc5a2c064b2
