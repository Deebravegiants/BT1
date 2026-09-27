# [H] CVE-2017-17125

## Summary
Severity: High
Advisory: CVE-2017-17125
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-04
Source: https://osv.dev/vulnerability/CVE-2017-17125
Type: osv

## Details
nm.c and objdump.c in GNU Binutils 2.29.1 mishandle certain global symbols, which allows remote attackers to cause a denial of service (_bfd_elf_get_symbol_version_string buffer over-read and application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=160b1a618ad94988410dc81fce9189fcda5b7ff4
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22443
