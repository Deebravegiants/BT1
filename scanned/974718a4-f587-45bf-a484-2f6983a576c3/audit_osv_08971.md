# [C] CVE-2016-7124

## Summary
Severity: Critical
Advisory: CVE-2016-7124
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7124
Type: osv

## Details
ext/standard/var_unserializer.c in PHP before 5.6.25 and 7.x before 7.0.10 mishandles certain invalid objects, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via crafted serialized data that leads to a (1) __destruct call or (2) magic method call.

## References
- http://www.securityfocus.com/bid/92756
- http://www.securitytracker.com/id/1036680
- https://www.tenable.com/security/tns-2016-19
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72663
- https://github.com/php/php-src/commit/20ce2fe8e3c211a42fee05a461a5881be9a8790e?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
