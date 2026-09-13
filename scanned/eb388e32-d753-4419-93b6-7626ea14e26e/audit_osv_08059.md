# [C] CVE-2016-10160

## Summary
Severity: Critical
Advisory: CVE-2016-10160
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-24
Source: https://osv.dev/vulnerability/CVE-2016-10160
Type: osv

## Details
Off-by-one error in the phar_parse_pharfile function in ext/phar/phar.c in PHP before 5.6.30 and 7.0.x before 7.0.15 allows remote attackers to cause a denial of service (memory corruption) or possibly execute arbitrary code via a crafted PHAR archive with an alias mismatch.

## References
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.debian.org/security/2017/dsa-3783
- http://www.securityfocus.com/bid/95783
- http://www.securitytracker.com/id/1037659
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201702-29
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.tenable.com/security/tns-2017-04
- https://bugs.php.net/bug.php?id=73768
- https://github.com/php/php-src/commit/b28b8b2fee6dfa6fcd13305c581bb835689ac3be
