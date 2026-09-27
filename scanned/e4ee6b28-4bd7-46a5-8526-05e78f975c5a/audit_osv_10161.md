# [M] CVE-2017-14129

## Summary
Severity: Medium
Advisory: CVE-2017-14129
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14129
Type: osv

## Details
The read_section function in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (parse_comp_unit heap-based buffer over-read and application crash) via a crafted ELF file.

## References
- http://www.securityfocus.com/bid/100624
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=e4f2723003859dc6b33ca0dadbc4a7659ebf1643
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=22047
