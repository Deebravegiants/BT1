# [M] CVE-2017-14940

## Summary
Severity: Medium
Advisory: CVE-2017-14940
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14940
Type: osv

## Details
scan_unit_for_symbols in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=0d76029f92182c3682d8be2c833d45bc9a2068fe
- https://blogs.gentoo.org/ago/2017/09/26/binutils-null-pointer-dereference-in-scan_unit_for_symbols-dwarf2-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22166
