# [M] CVE-2017-14128

## Summary
Severity: Medium
Advisory: CVE-2017-14128
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-04
Source: https://osv.dev/vulnerability/CVE-2017-14128
Type: osv

## Details
The decode_line_info function in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (read_1_byte heap-based buffer over-read and application crash) via a crafted ELF file.

## References
- http://www.securityfocus.com/bid/100623
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=7e8b60085eb3e6f2c41bc0c00c0d759fa7f72780
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=22059
