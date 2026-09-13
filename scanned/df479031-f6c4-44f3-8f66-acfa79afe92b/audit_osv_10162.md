# [M] CVE-2017-14130

## Summary
Severity: Medium
Advisory: CVE-2017-14130
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14130
Type: osv

## Details
The _bfd_elf_parse_attributes function in elf-attrs.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (_bfd_elf_attr_strdup heap-based buffer over-read and application crash) via a crafted ELF file.

## References
- http://www.securityfocus.com/bid/100625
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=2a143b99fc4a5094a9cf128f3184d8e6818c8229
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=22058
