# [H] CVE-2017-16829

## Summary
Severity: High
Advisory: CVE-2017-16829
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16829
Type: osv

## Details
The _bfd_elf_parse_gnu_properties function in elf-properties.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, does not prevent negative pointers, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=cf54ebff3b7361989712fd9c0128a9b255578163
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22307
