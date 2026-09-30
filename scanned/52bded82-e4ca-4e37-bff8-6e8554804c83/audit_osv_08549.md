# [C] CVE-2016-4346

## Summary
Severity: Critical
Advisory: CVE-2016-4346
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-22
Source: https://osv.dev/vulnerability/CVE-2016-4346
Type: osv

## Details
Integer overflow in the str_pad function in ext/standard/string.c in PHP before 7.0.4 allows remote attackers to cause a denial of service or possibly have unspecified other impact via a long string, leading to a heap-based buffer overflow.

## References
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00086.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00027.html
- http://php.net/ChangeLog-7.php
- http://www.openwall.com/lists/oss-security/2016/04/28/2
- https://bugs.php.net/bug.php?id=71637
