# [H] CVE-2016-4809

## Summary
Severity: High
Advisory: CVE-2016-4809
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-4809
Type: osv

## Details
The archive_read_format_cpio_read_header function in archive_read_support_format_cpio.c in libarchive before 3.2.1 allows remote attackers to cause a denial of service (application crash) via a CPIO archive with a large symlink.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://rhn.redhat.com/errata/RHSA-2016-1850.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91813
- https://security.gentoo.org/glsa/201701-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1347084
- https://github.com/libarchive/libarchive/commit/fd7e0c02
- https://github.com/libarchive/libarchive/issues/705
