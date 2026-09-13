# [M] CVE-2016-10350

## Summary
Severity: Medium
Advisory: CVE-2016-10350
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2016-10350
Type: osv

## Details
The archive_read_format_cab_read_header function in archive_read_support_format_cab.c in libarchive 3.2.2 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://usn.ubuntu.com/3736-1/
- https://security.gentoo.org/glsa/201710-19
- https://www.debian.org/security/2018/dsa-4360
- https://github.com/libarchive/libarchive/issues/835
