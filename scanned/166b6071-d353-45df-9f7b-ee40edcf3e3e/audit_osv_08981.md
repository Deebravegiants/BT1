# [C] CVE-2016-7134

## Summary
Severity: Critical
Advisory: CVE-2016-7134
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7134
Type: osv

## Details
ext/curl/interface.c in PHP 7.x before 7.0.10 does not work around a libcurl integer overflow, which allows remote attackers to cause a denial of service (allocation error and heap-based buffer overflow) or possibly have unspecified other impact via a long string that is mishandled in a curl_escape call.

## References
- http://www.securityfocus.com/bid/92766
- http://www.securitytracker.com/id/1036680
- http://www.php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=72674
- https://security.gentoo.org/glsa/201611-22
- https://github.com/php/php-src/commit/72dbb7f416160f490c4e9987040989a10ad431c7?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
