# [H] CVE-2016-10397

## Summary
Severity: High
Advisory: CVE-2016-10397
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2016-10397
Type: osv

## Details
In PHP before 5.6.28 and 7.x before 7.0.13, incorrect handling of various URI components in the URL parser could be used by attackers to bypass hostname-specific URL checks, as demonstrated by evil.example.com:80#@good.example.com/ and evil.example.com:80?@good.example.com/ inputs to the parse_url function (implemented in the php_url_parse_ex function in ext/standard/url.c).

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=b061fa909de77085d3822a89ab901b934d0362c4
- http://www.securityfocus.com/bid/99552
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://bugs.php.net/bug.php?id=73192
- http://openwall.com/lists/oss-security/2017/07/10/6
