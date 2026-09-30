# [H] CVE-2016-4343

## Summary
Severity: High
Advisory: CVE-2016-4343
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-22
Source: https://osv.dev/vulnerability/CVE-2016-4343
Type: osv

## Details
The phar_make_dirstream function in ext/phar/dirstream.c in PHP before 5.6.18 and 7.x before 7.0.3 mishandles zero-size ././@LongLink files, which allows remote attackers to cause a denial of service (uninitialized pointer dereference) or possibly have unspecified other impact via a crafted TAR archive.

## References
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00086.html
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.openwall.com/lists/oss-security/2016/04/28/2
- http://www.securityfocus.com/bid/89179
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05320149
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- https://bugs.php.net/bug.php?id=71331
