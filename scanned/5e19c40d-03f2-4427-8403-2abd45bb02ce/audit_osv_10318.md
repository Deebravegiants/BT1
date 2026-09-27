# [M] CVE-2017-14938

## Summary
Severity: Medium
Advisory: CVE-2017-14938
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14938
Type: osv

## Details
_bfd_elf_slurp_version_tables in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (excessive memory allocation and application crash) via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=bd61e135492ecf624880e6b78e5fcde3c9716df6
- http://www.securityfocus.com/bid/101212
- https://blogs.gentoo.org/ago/2017/09/26/binutils-memory-allocation-failure-in-_bfd_elf_slurp_version_tables-elf-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22166
