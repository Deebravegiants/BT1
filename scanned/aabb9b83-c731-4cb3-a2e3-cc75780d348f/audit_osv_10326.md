# [M] CVE-2017-14974

## Summary
Severity: Medium
Advisory: CVE-2017-14974
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14974
Type: osv

## Details
The *_get_synthetic_symtab functions in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, mishandle the failure of a certain canonicalization step, which allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted ELF file, related to elf32-i386.c and elf64-x86-64.c.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=e70c19e3a4c26e9c1ebf0c9170d105039b56d7cf
- https://sourceware.org/bugzilla/show_bug.cgi?id=22163
