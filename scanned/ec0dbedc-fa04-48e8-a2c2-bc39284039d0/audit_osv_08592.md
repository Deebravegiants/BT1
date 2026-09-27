# [C] CVE-2016-4544

## Summary
Severity: Critical
Advisory: CVE-2016-4544
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-22
Source: https://osv.dev/vulnerability/CVE-2016-4544
Type: osv

## Details
The exif_process_TIFF_in_JPEG function in ext/exif/exif.c in PHP before 5.5.35, 5.6.x before 5.6.21, and 7.x before 7.0.6 does not validate TIFF start data, which allows remote attackers to cause a denial of service (out-of-bounds read) or possibly have unspecified other impact via crafted header data.

## References
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=082aecfc3a753ad03be82cf14f03ac065723ec92
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183736.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00086.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00027.html
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3602
- http://www.securityfocus.com/bid/89844
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72094
- http://www.openwall.com/lists/oss-security/2016/05/05/21
