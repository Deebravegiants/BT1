# [H] CVE-2016-7133

## Summary
Severity: High
Advisory: CVE-2016-7133
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7133
Type: osv

## Details
Zend/zend_alloc.c in PHP 7.x before 7.0.10, when open_basedir is enabled, mishandles huge realloc operations, which allows remote attackers to cause a denial of service (integer overflow) or possibly have unspecified other impact via a long pathname.

## References
- http://www.securityfocus.com/bid/92765
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72742
- https://github.com/php/php-src/commit/c2a13ced4272f2e65d2773e2ea6ca11c1ce4a911?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
