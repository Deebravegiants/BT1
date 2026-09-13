# [H] CVE-2016-5096

## Summary
Severity: High
Advisory: CVE-2016-5096
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5096
Type: osv

## Details
Integer overflow in the fread function in ext/standard/file.c in PHP before 5.5.36 and 5.6.x before 5.6.22 allows remote attackers to cause a denial of service or possibly have unspecified other impact via a large integer in the second argument.

## References
- http://www.securityfocus.com/bid/90861
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3602
- http://www.openwall.com/lists/oss-security/2016/05/26/3
- http://php.net/ChangeLog-5.php
- https://github.com/php/php-src/commit/abd159cce48f3e34f08e4751c568e09677d5ec9c?w=1
- https://bugs.php.net/bug.php?id=72114
