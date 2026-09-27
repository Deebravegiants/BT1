# [C] CVE-2016-7414

## Summary
Severity: Critical
Advisory: CVE-2016-7414
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/CVE-2016-7414
Type: osv

## Details
The ZIP signature-verification feature in PHP before 5.6.26 and 7.x before 7.0.11 does not ensure that the uncompressed_filesize field is large enough, which allows remote attackers to cause a denial of service (out-of-bounds memory access) or possibly have unspecified other impact via a crafted PHAR archive, related to ext/phar/util.c and ext/phar/zip.c.

## References
- http://www.securityfocus.com/bid/93004
- http://www.securitytracker.com/id/1036836
- https://www.tenable.com/security/tns-2016-19
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72928
- https://github.com/php/php-src/commit/0bfb970f43acd1e81d11be1154805f86655f15d5?w=1
- http://www.openwall.com/lists/oss-security/2016/09/15/10
