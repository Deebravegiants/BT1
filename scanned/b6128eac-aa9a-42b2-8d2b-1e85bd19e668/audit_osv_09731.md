# [C] CVE-2017-11147

## Summary
Severity: Critical
Advisory: CVE-2017-11147
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11147
Type: osv

## Details
In PHP before 5.6.30 and 7.x before 7.0.15, the PHAR archive handler could be used by attackers supplying malicious archive files to crash the PHP interpreter or potentially disclose information due to a buffer over-read in the phar_parse_pharfile function in ext/phar/phar.c.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=e5246580a85f031e1a3b8064edbaa55c1643a451
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/99607
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.tenable.com/security/tns-2017-12
- https://bugs.php.net/bug.php?id=73773
- http://openwall.com/lists/oss-security/2017/07/10/6
