# [H] CVE-2016-7125

## Summary
Severity: High
Advisory: CVE-2016-7125
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7125
Type: osv

## Details
ext/session/session.c in PHP before 5.6.25 and 7.x before 7.0.10 skips invalid session names in a way that triggers incorrect parsing, which allows remote attackers to inject arbitrary-type session data by leveraging control of a session name, as demonstrated by object injection.

## References
- http://www.securityfocus.com/bid/92552
- http://www.securitytracker.com/id/1036680
- https://www.tenable.com/security/tns-2016-19
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72681
- https://github.com/php/php-src/commit/8763c6090d627d8bb0ee1d030c30e58f406be9ce?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
