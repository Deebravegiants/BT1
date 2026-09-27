# [C] CVE-2016-7126

## Summary
Severity: Critical
Advisory: CVE-2016-7126
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7126
Type: osv

## Details
The imagetruecolortopalette function in ext/gd/gd.c in PHP before 5.6.25 and 7.x before 7.0.10 does not properly validate the number of colors, which allows remote attackers to cause a denial of service (select_colors allocation error and out-of-bounds write) or possibly have unspecified other impact via a large value in the third argument.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/92755
- http://www.securitytracker.com/id/1036680
- https://security.gentoo.org/glsa/201611-22
- https://www.tenable.com/security/tns-2016-19
- https://bugs.php.net/bug.php?id=72697
- https://github.com/php/php-src/commit/28022c9b1fd937436ab67bb3d61f652c108baf96
- https://github.com/php/php-src/commit/b6f13a5ef9d6280cf984826a5de012a32c396cd4?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
