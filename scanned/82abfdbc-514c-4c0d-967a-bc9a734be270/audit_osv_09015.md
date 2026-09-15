# [C] CVE-2016-7417

## Summary
Severity: Critical
Advisory: CVE-2016-7417
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/CVE-2016-7417
Type: osv

## Details
ext/spl/spl_array.c in PHP before 5.6.26 and 7.x before 7.0.11 proceeds with SplArray unserialization without validating a return value and data type, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via crafted serialized data.

## References
- http://www.securityfocus.com/bid/93007
- http://www.securitytracker.com/id/1036836
- https://www.tenable.com/security/tns-2016-19
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=73029
- https://github.com/php/php-src/commit/ecb7f58a069be0dec4a6131b6351a761f808f22e?w=1
- http://www.openwall.com/lists/oss-security/2016/09/15/10
