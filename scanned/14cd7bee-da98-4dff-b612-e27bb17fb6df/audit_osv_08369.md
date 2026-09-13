# [C] CVE-2016-2554

## Summary
Severity: Critical
Advisory: CVE-2016-2554
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-16
Source: https://osv.dev/vulnerability/CVE-2016-2554
Type: osv

## Details
Stack-based buffer overflow in ext/phar/tar.c in PHP before 5.5.32, 5.6.x before 5.6.18, and 7.x before 7.0.3 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted TAR archive.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00058.html
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.ubuntu.com/usn/USN-2952-1
- http://www.ubuntu.com/usn/USN-2952-2
- https://bugs.php.net/bug.php?id=71488
