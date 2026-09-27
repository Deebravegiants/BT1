# [H] CVE-2016-5767

## Summary
Severity: High
Advisory: CVE-2016-5767
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5767
Type: osv

## Details
Integer overflow in the gdImageCreate function in gd.c in the GD Graphics Library (aka libgd) before 2.0.34RC1, as used in PHP before 5.5.37, 5.6.x before 5.6.23, and 7.x before 7.0.8, allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted image dimensions.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00025.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00003.html
- http://www.securityfocus.com/bid/91395
- https://bugs.php.net/bug.php?id=72446
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2598.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.openwall.com/lists/oss-security/2016/06/23/4
- http://github.com/php/php-src/commit/c395c6e5d7e8df37a21265ff76e48fe75ceb5ae6?w=1
