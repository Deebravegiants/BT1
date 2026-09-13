# [H] CVE-2017-12459

## Summary
Severity: High
Advisory: CVE-2017-12459
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12459
Type: osv

## Details
The bfd_mach_o_read_symtab_strtab function in bfd/mach-o.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29 and earlier, allows remote attackers to cause an out of bounds heap write and possibly achieve code execution via a crafted mach-o file.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=21840
