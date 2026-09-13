# [C] CVE-2016-9935

## Summary
Severity: Critical
Advisory: CVE-2016-9935
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-9935
Type: osv

## Details
The php_wddx_push_element function in ext/wddx/wddx.c in PHP before 5.6.29 and 7.x before 7.0.14 allows remote attackers to cause a denial of service (out-of-bounds read and memory corruption) or possibly have unspecified other impact via an empty boolean element in a wddxPacket XML document.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00142.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00034.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00054.html
- http://www.securityfocus.com/bid/94846
- http://www.debian.org/security/2016/dsa-3737
- http://www.openwall.com/lists/oss-security/2016/12/12/2
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://bugs.php.net/bug.php?id=73631
- https://security.gentoo.org/glsa/201702-29
- https://github.com/php/php-src/commit/66fd44209d5ffcb9b3d1bc1b9fd8e35b485040c0
