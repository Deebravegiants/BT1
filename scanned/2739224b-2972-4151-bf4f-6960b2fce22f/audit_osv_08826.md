# [C] CVE-2016-6288

## Summary
Severity: Critical
Advisory: CVE-2016-6288
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6288
Type: osv

## Details
The php_url_parse_ex function in ext/standard/url.c in PHP before 5.5.38 allows remote attackers to cause a denial of service (buffer over-read) or possibly have unspecified other impact via vectors involving the smart_str data type.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=629e4da7cc8b174acdeab84969cbfc606a019b31
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://www.securitytracker.com/id/1036430
- https://support.apple.com/HT207170
- http://php.net/ChangeLog-5.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.securityfocus.com/bid/92111
- https://bugs.php.net/70480
- http://openwall.com/lists/oss-security/2016/07/24/2
