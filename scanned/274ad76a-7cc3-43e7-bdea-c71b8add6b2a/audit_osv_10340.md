# [M] CVE-2017-15025

## Summary
Severity: Medium
Advisory: CVE-2017-15025
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15025
Type: osv

## Details
decode_line_info in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=d8010d3e75ec7194a4703774090b27486b742d48
- https://blogs.gentoo.org/ago/2017/10/03/binutils-divide-by-zero-in-decode_line_info-dwarf2-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22186
