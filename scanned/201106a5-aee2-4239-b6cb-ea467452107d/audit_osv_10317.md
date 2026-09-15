# [M] CVE-2017-14934

## Summary
Severity: Medium
Advisory: CVE-2017-14934
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14934
Type: osv

## Details
process_debug_info in dwarf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (infinite loop) via a crafted ELF file that contains a negative size value in a CU structure.

## References
- http://www.securityfocus.com/bid/101204
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=19485196044b2521af979f1e5c4a89bfb90fba0b
- https://sourceware.org/bugzilla/show_bug.cgi?id=22219
