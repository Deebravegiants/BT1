# [H] CVE-2017-14745

## Summary
Severity: High
Advisory: CVE-2017-14745
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-26
Source: https://osv.dev/vulnerability/CVE-2017-14745
Type: osv

## Details
The *_get_synthetic_symtab functions in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, interpret a -1 value as a sorting count instead of an error flag, which allows remote attackers to cause a denial of service (integer overflow and application crash) or possibly have unspecified other impact via a crafted ELF file, related to elf32-i386.c and elf64-x86-64.c.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=22148
