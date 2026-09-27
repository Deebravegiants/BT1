# [C] CVE-2018-7584

## Summary
Severity: Critical
Advisory: CVE-2018-7584
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2018-7584
Type: osv

## Details
In PHP through 5.6.33, 7.0.x before 7.0.28, 7.1.x through 7.1.14, and 7.2.x through 7.2.2, there is a stack-based buffer under-read while parsing an HTTP response in the php_stream_url_wrap_http_ex function in ext/standard/http_fopen_wrapper.c. This subsequently results in copying a large string.

## References
- http://php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/103204
- http://www.securitytracker.com/id/1041607
- https://access.redhat.com/errata/RHSA-2019:2519
- https://lists.debian.org/debian-lts-announce/2018/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00005.html
- https://usn.ubuntu.com/3600-1/
- https://usn.ubuntu.com/3600-2/
- https://www.debian.org/security/2018/dsa-4240
- https://www.tenable.com/security/tns-2018-03
- https://www.tenable.com/security/tns-2018-12
- https://bugs.php.net/bug.php?id=75981
- https://github.com/php/php-src/commit/523f230c831d7b33353203fa34aee4e92ac12bba
- https://www.exploit-db.com/exploits/44846/
