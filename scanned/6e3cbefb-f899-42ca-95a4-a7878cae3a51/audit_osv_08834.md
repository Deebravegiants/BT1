# [C] CVE-2016-6296

## Summary
Severity: Critical
Advisory: CVE-2016-6296
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6296
Type: osv

## Details
Integer signedness error in the simplestring_addn function in simplestring.c in xmlrpc-epi through 0.54.2, as used in PHP before 5.5.38, 5.6.x before 5.6.24, and 7.x before 7.0.9, allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via a long first argument to the PHP xmlrpc_encode_request function.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=e6c48213c22ed50b2b987b479fcc1ac709394caa
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://www.securitytracker.com/id/1036430
- https://lists.debian.org/debian-lts-announce/2019/11/msg00029.html
- https://support.apple.com/HT207170
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.securityfocus.com/bid/92095
- http://www.ubuntu.com/usn/USN-3059-1
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/72606
- http://openwall.com/lists/oss-security/2016/07/24/2
