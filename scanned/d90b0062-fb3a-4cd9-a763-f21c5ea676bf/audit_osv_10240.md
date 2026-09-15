# [H] CVE-2017-14502

## Summary
Severity: High
Advisory: CVE-2017-14502
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14502
Type: osv

## Details
read_header in archive_read_support_format_rar.c in libarchive 3.3.2 suffers from an off-by-one error for UTF-16 names in RAR archives, leading to an out-of-bounds read in archive_read_format_rar_read_header.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://usn.ubuntu.com/3859-1/
- https://github.com/libarchive/libarchive/commit/5562545b5562f6d12a4ef991fae158bf4ccf92b6
- https://security.gentoo.org/glsa/201908-11
- https://www.debian.org/security/2018/dsa-4360
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=573
- https://bugs.debian.org/875974
