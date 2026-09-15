# [C] CVE-2016-7480

## Summary
Severity: Critical
Advisory: CVE-2016-7480
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-11
Source: https://osv.dev/vulnerability/CVE-2016-7480
Type: osv

## Details
The SplObjectStorage unserialize implementation in ext/spl/spl_observer.c in PHP before 7.0.12 does not verify that a key is an object, which allows remote attackers to execute arbitrary code or cause a denial of service (uninitialized memory access) via crafted serialized data.

## References
- http://blog.checkpoint.com/2016/12/27/check-point-discovers-three-zero-day-vulnerabilities-web-programming-language-php-7
- http://php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/95152
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.youtube.com/watch?v=LDcaPstAuPk
- https://bugs.php.net/bug.php?id=73257
- https://github.com/php/php-src/commit/61cdd1255d5b9c8453be71aacbbf682796ac77d4
- http://blog.checkpoint.com/wp-content/uploads/2016/12/PHP_Technical_Report.pdf
