# [C] CVE-2016-6290

## Summary
Severity: Critical
Advisory: CVE-2016-6290
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6290
Type: osv

## Details
ext/session/session.c in PHP before 5.5.38, 5.6.x before 5.6.24, and 7.x before 7.0.9 does not properly maintain a certain hash data structure, which allows remote attackers to cause a denial of service (use-after-free) or possibly have unspecified other impact via vectors related to session deserialization.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=3798eb6fd5dddb211b01d41495072fd9858d4e32
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://php.net/ChangeLog-7.php
- http://www.securitytracker.com/id/1036430
- https://support.apple.com/HT207170
- http://openwall.com/lists/oss-security/2016/07/24/2
- http://php.net/ChangeLog-5.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.securityfocus.com/bid/92097
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/72562
