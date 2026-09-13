# [M] CVE-2017-13757

## Summary
Severity: Medium
Advisory: CVE-2017-13757
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13757
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, does not validate the PLT section size, which allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file, related to elf_i386_get_synthetic_symtab in elf32-i386.c and elf_x86_64_get_synthetic_symtab in elf64-x86-64.c.

## References
- http://www.securityfocus.com/bid/100532
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=90efb6422939ca031804266fba669f77c22a274a
- https://sourceware.org/bugzilla/show_bug.cgi?id=22018
