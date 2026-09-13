# [H] CVE-2017-11144

## Summary
Severity: High
Advisory: CVE-2017-11144
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11144
Type: osv

## Details
In PHP before 5.6.31, 7.x before 7.0.21, and 7.1.x before 7.1.7, the openssl extension PEM sealing code did not check the return value of the OpenSSL sealing function, which could lead to a crash of the PHP interpreter, related to an interpretation conflict for a negative number in ext/openssl/openssl.c, and an OpenSSL documentation omission.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=73cabfedf519298e1a11192699f44d53c529315e
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=89637c6b41b510c20d262c17483f582f115c66d6
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=91826a311dd37f4c4e5d605fa7af331e80ddd4c3
- https://www.tenable.com/security/tns-2017-12
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://bugs.php.net/bug.php?id=74651
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.debian.org/security/2018/dsa-4080
- https://www.debian.org/security/2018/dsa-4081
- http://openwall.com/lists/oss-security/2017/07/10/6
