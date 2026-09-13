# [M] CVE-2017-15021

## Summary
Severity: Medium
Advisory: CVE-2017-15021
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15021
Type: osv

## Details
bfd_get_debug_link_info_1 in opncls.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file, related to bfd_getl32.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=52b36c51e5bf6d7600fdc6ba115b170b0e78e31d
- https://blogs.gentoo.org/ago/2017/10/03/binutils-heap-based-buffer-overflow-in-bfd_getl32-opncls-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22197
