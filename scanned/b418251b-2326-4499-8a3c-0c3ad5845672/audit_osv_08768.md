# [C] CVE-2016-5769

## Summary
Severity: Critical
Advisory: CVE-2016-5769
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5769
Type: osv

## Details
Multiple integer overflows in mcrypt.c in the mcrypt extension in PHP before 5.5.37, 5.6.x before 5.6.23, and 7.x before 7.0.8 allow remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted length value, related to the (1) mcrypt_generic and (2) mdecrypt_generic functions.

## References
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00025.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00003.html
- http://php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/91399
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://support.apple.com/HT207170
- http://www.debian.org/security/2016/dsa-3618
- http://www.openwall.com/lists/oss-security/2016/06/23/4
- https://bugs.php.net/bug.php?id=72455
- http://github.com/php/php-src/commit/6c5211a0cef0cc2854eaa387e0eb036e012904d0?w=1
- http://php.net/ChangeLog-5.php
