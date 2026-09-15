# [H] CVE-2017-12452

## Summary
Severity: High
Advisory: CVE-2017-12452
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12452
Type: osv

## Details
The bfd_mach_o_i386_canonicalize_one_reloc function in bfd/mach-o-i386.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29 and earlier, allows remote attackers to cause an out of bounds heap read via a crafted mach-o file.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=21813
