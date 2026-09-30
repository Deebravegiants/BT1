# [C] CVE-2016-6294

## Summary
Severity: Critical
Advisory: CVE-2016-6294
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6294
Type: osv

## Details
The locale_accept_from_http function in ext/intl/locale/locale_methods.c in PHP before 5.5.38, 5.6.x before 5.6.24, and 7.x before 7.0.9 does not properly restrict calls to the ICU uloc_acceptLanguageFromHTTP function, which allows remote attackers to cause a denial of service (out-of-bounds read) or possibly have unspecified other impact via a call with a long argument.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=aa82e99ed8003c01f1ef4f0940e56b85c5b032d4
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://www.securitytracker.com/id/1036430
- https://support.apple.com/HT207170
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.securityfocus.com/bid/92115
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/72533
- http://openwall.com/lists/oss-security/2016/07/24/2
