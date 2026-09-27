# [M] CVE-2017-15225

## Summary
Severity: Medium
Advisory: CVE-2017-15225
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15225
Type: osv

## Details
_bfd_dwarf2_cleanup_debug_info in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (memory leak) via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=b55ec8b676ed05d93ee49d6c79ae0403616c4fb0
- https://sourceware.org/bugzilla/show_bug.cgi?id=22212
