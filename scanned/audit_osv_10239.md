# [M] CVE-2017-14501

## Summary
Severity: Medium
Advisory: CVE-2017-14501
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14501
Type: osv

## Details
An out-of-bounds read flaw exists in parse_file_info in archive_read_support_format_iso9660.c in libarchive 3.3.2 when extracting a specially crafted iso9660 iso file, related to archive_read_format_iso9660_read_header.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://usn.ubuntu.com/3736-1/
- https://github.com/libarchive/libarchive/issues/949
- https://security.gentoo.org/glsa/201908-11
- https://www.debian.org/security/2018/dsa-4360
- https://bugs.debian.org/875966
