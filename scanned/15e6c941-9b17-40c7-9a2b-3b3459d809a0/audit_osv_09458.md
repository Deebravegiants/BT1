# [H] CVE-2016-9934

## Summary
Severity: High
Advisory: CVE-2016-9934
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-9934
Type: osv

## Details
ext/wddx/wddx.c in PHP before 5.6.28 and 7.x before 7.0.13 allows remote attackers to cause a denial of service (NULL pointer dereference) via crafted serialized data in a wddxPacket XML document, as demonstrated by a PDORow string.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00142.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00034.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00054.html
- http://www.securityfocus.com/bid/94845
- http://www.openwall.com/lists/oss-security/2016/12/12/2
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://bugs.php.net/bug.php?id=73331
- https://github.com/php/php-src/commit/6045de69c7dedcba3eadf7c4bba424b19c81d00d
