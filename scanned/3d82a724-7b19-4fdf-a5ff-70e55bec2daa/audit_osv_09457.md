# [H] CVE-2016-9933

## Summary
Severity: High
Advisory: CVE-2016-9933
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-9933
Type: osv

## Details
Stack consumption vulnerability in the gdImageFillToBorder function in gd.c in the GD Graphics Library (aka libgd) before 2.2.2, as used in PHP before 5.6.28 and 7.x before 7.0.13, allows remote attackers to cause a denial of service (segmentation violation) via a crafted imagefilltoborder call that triggers use of a negative color value.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00133.html
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00142.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00002.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00034.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00054.html
- http://www.securityfocus.com/bid/94865
- http://www.debian.org/security/2017/dsa-3751
- http://www.openwall.com/lists/oss-security/2016/12/12/2
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://bugs.php.net/bug.php?id=72696
- https://github.com/libgd/libgd/issues/215
- https://github.com/php/php-src/commit/863d37ea66d5c960db08d6f4a2cbd2518f0f80d1
- https://github.com/libgd/libgd/commit/77f619d48259383628c3ec4654b1ad578e9eb40e
