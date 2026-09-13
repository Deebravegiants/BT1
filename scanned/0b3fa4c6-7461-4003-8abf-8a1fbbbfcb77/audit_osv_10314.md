# [M] CVE-2017-14930

## Summary
Severity: Medium
Advisory: CVE-2017-14930
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14930
Type: osv

## Details
Memory leak in decode_line_info in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (memory consumption) via a crafted ELF file.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=22191
