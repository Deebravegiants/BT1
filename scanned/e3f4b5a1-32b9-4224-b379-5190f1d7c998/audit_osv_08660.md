# [H] CVE-2016-5094

## Summary
Severity: High
Advisory: CVE-2016-5094
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5094
Type: osv

## Details
Integer overflow in the php_html_entities function in ext/standard/html.c in PHP before 5.5.36 and 5.6.x before 5.6.22 allows remote attackers to cause a denial of service or possibly have unspecified other impact by triggering a large output string from the htmlspecialchars function.

## References
- http://www.securityfocus.com/bid/90857
- https://bugs.php.net/bug.php?id=72135
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- http://php.net/ChangeLog-5.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3602
- http://www.openwall.com/lists/oss-security/2016/05/26/3
- https://github.com/php/php-src/commit/0da8b8b801f9276359262f1ef8274c7812d3dfda?w=1
