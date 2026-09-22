# [M] CVE-2018-14851

## Summary
Severity: Medium
Advisory: CVE-2018-14851
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-02
Source: https://osv.dev/vulnerability/CVE-2018-14851
Type: osv

## Details
exif_process_IFD_in_MAKERNOTE in ext/exif/exif.c in PHP before 5.6.37, 7.0.x before 7.0.31, 7.1.x before 7.1.20, and 7.2.x before 7.2.8 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted JPEG file.

## References
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/104871
- https://access.redhat.com/errata/RHSA-2019:2519
- https://lists.debian.org/debian-lts-announce/2018/09/msg00000.html
- https://security.netapp.com/advisory/ntap-20181107-0003/
- https://usn.ubuntu.com/3766-1/
- https://usn.ubuntu.com/3766-2/
- https://www.debian.org/security/2018/dsa-4353
- https://www.tenable.com/security/tns-2018-12
- https://bugs.php.net/bug.php?id=76557
