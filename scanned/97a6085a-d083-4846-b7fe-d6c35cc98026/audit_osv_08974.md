# [C] CVE-2016-7127

## Summary
Severity: Critical
Advisory: CVE-2016-7127
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7127
Type: osv

## Details
The imagegammacorrect function in ext/gd/gd.c in PHP before 5.6.25 and 7.x before 7.0.10 does not properly validate gamma values, which allows remote attackers to cause a denial of service (out-of-bounds write) or possibly have unspecified other impact by providing different signs for the second and third arguments.

## References
- http://www.securityfocus.com/bid/92757
- http://www.securitytracker.com/id/1036680
- https://www.tenable.com/security/tns-2016-19
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72730
- https://github.com/php/php-src/commit/1bd103df00f49cf4d4ade2cfe3f456ac058a4eae?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
