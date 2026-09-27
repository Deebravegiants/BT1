# [M] CVE-2017-14107

## Summary
Severity: Medium
Advisory: CVE-2017-14107
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-01
Source: https://osv.dev/vulnerability/CVE-2017-14107
Type: osv

## Details
The _zip_read_eocd64 function in zip_open.c in libzip before 1.3.0 mishandles EOCD records, which allows remote attackers to cause a denial of service (memory allocation failure in _zip_cdir_grow in zip_dirent.c) via a crafted ZIP archive.

## References
- https://lists.debian.org/debian-lts-announce/2021/12/msg00022.html
- https://blogs.gentoo.org/ago/2017/09/01/libzip-memory-allocation-failure-in-_zip_cdir_grow-zip_dirent-c/
- https://github.com/nih-at/libzip/commit/9b46957ec98d85a572e9ef98301247f39338a3b5
