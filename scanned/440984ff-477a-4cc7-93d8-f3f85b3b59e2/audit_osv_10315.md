# [M] CVE-2017-14932

## Summary
Severity: Medium
Advisory: CVE-2017-14932
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14932
Type: osv

## Details
decode_line_info in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (infinite loop) via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=e338894dc2e603683bed2172e8e9f25b29051005
- https://sourceware.org/bugzilla/show_bug.cgi?id=22204
