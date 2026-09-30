# [H] CVE-2017-11628

## Summary
Severity: High
Advisory: CVE-2017-11628
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-11628
Type: osv

## Details
In PHP before 5.6.31, 7.x before 7.0.21, and 7.1.x before 7.1.7, a stack-based buffer overflow in the zend_ini_do_op() function in Zend/zend_ini_parser.c could cause a denial of service or potentially allow executing code. NOTE: this is only relevant for PHP applications that accept untrusted input (instead of the system's php.ini file) for the parse_ini_string or parse_ini_file function, e.g., a web application for syntax validation of php.ini directives.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=05255749139b3686c8a6a58ee01131ac0047465e
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=5f8380d33e648964d2d5140f329cf2d4c443033c
- http://www.securityfocus.com/bid/99489
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201709-21
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.debian.org/security/2018/dsa-4080
- https://www.debian.org/security/2018/dsa-4081
- https://bugs.php.net/bug.php?id=74603
