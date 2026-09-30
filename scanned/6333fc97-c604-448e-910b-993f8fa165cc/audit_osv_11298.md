# [M] CVE-2017-7299

## Summary
Severity: Medium
Advisory: CVE-2017-7299
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7299
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, has an invalid read (of size 8) because the code to emit relocs (bfd_elf_final_link function in bfd/elflink.c) does not check the format of the input file before trying to read the ELF reloc section header. The vulnerability leads to a GNU linker (ld) program crash.

## References
- http://www.securityfocus.com/bid/97217
- https://sourceware.org/bugzilla/show_bug.cgi?id=20908
