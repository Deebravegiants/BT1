# [C] CVE-2016-4538

## Summary
Severity: Critical
Advisory: CVE-2016-4538
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-22
Source: https://osv.dev/vulnerability/CVE-2016-4538
Type: osv

## Details
The bcpowmod function in ext/bcmath/bcmath.c in PHP before 5.5.35, 5.6.x before 5.6.21, and 7.x before 7.0.6 modifies certain data structures without considering whether they are copies of the _zero_, _one_, or _two_ global variable, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted call.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183736.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00086.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00027.html
- http://www.openwall.com/lists/oss-security/2016/05/05/21
- http://www.securityfocus.com/bid/90173
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=d650063a0457aec56364e4005a636dc6c401f9cd
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05320149
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3602
- https://security.gentoo.org/glsa/201611-22
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=72093
