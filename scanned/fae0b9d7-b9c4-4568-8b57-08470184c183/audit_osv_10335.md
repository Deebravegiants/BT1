# [H] CVE-2017-15020

## Summary
Severity: High
Advisory: CVE-2017-15020
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15020
Type: osv

## Details
dwarf1.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, mishandles pointers, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted ELF file, related to parse_die and parse_line_table, as demonstrated by a parse_die heap-based buffer over-read.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=1da5c9a485f3dcac4c45e96ef4b7dae5948314b5
- https://blogs.gentoo.org/ago/2017/10/03/binutils-heap-based-buffer-overflow-in-parse_die-dwarf1-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22202
