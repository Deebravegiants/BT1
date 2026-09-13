# [H] CVE-2016-3142

## Summary
Severity: High
Advisory: CVE-2016-3142
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-03-31
Source: https://osv.dev/vulnerability/CVE-2016-3142
Type: osv

## Details
The phar_parse_zipfile function in zip.c in the PHAR extension in PHP before 5.5.33 and 5.6.x before 5.6.19 allows remote attackers to obtain sensitive information from process memory or cause a denial of service (out-of-bounds read and application crash) by placing a PK\x05\x06 signature at an invalid location.

## References
- http://lists.apple.com/archives/security-announce/2016/May/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00058.html
- http://www.securitytracker.com/id/1035255
- https://bugs.php.net/bug.php?id=71498
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=a6fdc5bb27b20d889de0cd29318b3968aabb57bd
- https://php.net/ChangeLog-5.php
- https://support.apple.com/HT206567
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.ubuntu.com/usn/USN-2952-1
- http://www.ubuntu.com/usn/USN-2952-2
