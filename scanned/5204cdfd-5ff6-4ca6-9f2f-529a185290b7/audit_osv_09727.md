# [H] CVE-2017-11142

## Summary
Severity: High
Advisory: CVE-2017-11142
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-10
Source: https://osv.dev/vulnerability/CVE-2017-11142
Type: osv

## Details
In PHP before 5.6.31, 7.x before 7.0.17, and 7.1.x before 7.1.3, remote attackers could cause a CPU consumption denial of service attack by injecting long form variables, related to main/php_variables.c.

## References
- http://www.securityfocus.com/bid/99601
- https://www.tenable.com/security/tns-2017-12
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=73807
- https://security.netapp.com/advisory/ntap-20180112-0001/
- https://www.debian.org/security/2018/dsa-4081
- https://github.com/php/php-src/commit/0f8cf3b8497dc45c010c44ed9e96518e11e19fc3
- https://github.com/php/php-src/commit/a15bffd105ac28fd0dd9b596632dbf035238fda3
- http://openwall.com/lists/oss-security/2017/07/10/6
