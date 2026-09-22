# [C] CVE-2016-3141

## Summary
Severity: Critical
Advisory: CVE-2016-3141
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-03-31
Source: https://osv.dev/vulnerability/CVE-2016-3141
Type: osv

## Details
Use-after-free vulnerability in wddx.c in the WDDX extension in PHP before 5.5.33 and 5.6.x before 5.6.19 allows remote attackers to cause a denial of service (memory corruption and application crash) or possibly have unspecified other impact by triggering a wddx_deserialize call on XML data containing a crafted var element.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=b1bd4119bcafab6f9a8f84d92cd65eec3afeface
- http://lists.apple.com/archives/security-announce/2016/May/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00058.html
- http://www.oracle.com/technetwork/topics/security/bulletinoct2016-3090566.html
- http://www.securityfocus.com/bid/84271
- http://www.securitytracker.com/id/1035255
- https://bugs.php.net/bug.php?id=71587
- https://php.net/ChangeLog-5.php
- https://support.apple.com/HT206567
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.ubuntu.com/usn/USN-2952-1
- http://www.ubuntu.com/usn/USN-2952-2
