# [H] CVE-2017-11145

## Summary
Severity: High
Advisory: CVE-2017-11145
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11145
Type: osv

## Details
In PHP before 5.6.31, 7.x before 7.0.21, and 7.1.x before 7.1.7, an error in the date extension's timelib_meridian parsing code could be used by attackers able to supply date strings to leak information from the interpreter, related to ext/date/lib/parse_date.c out-of-bounds reads affecting the php_parse_date function. NOTE: the correct fix is in the e8b7698f5ee757ce2c8bd10a192a491a498f891c commit, not the bd77ac90d3bdf31ce2a5251ad92e9e75 gist.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=e8b7698f5ee757ce2c8bd10a192a491a498f891c
- http://www.securityfocus.com/bid/99550
- https://www.tenable.com/security/tns-2017-12
- http://openwall.com/lists/oss-security/2017/07/10/6
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://bugs.php.net/bug.php?id=74819
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.debian.org/security/2018/dsa-4080
- https://www.debian.org/security/2018/dsa-4081
- https://gist.github.com/anonymous/bd77ac90d3bdf31ce2a5251ad92e9e75
