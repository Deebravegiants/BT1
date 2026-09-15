# [H] CVE-2017-12453

## Summary
Severity: High
Advisory: CVE-2017-12453
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12453
Type: osv

## Details
The _bfd_vms_slurp_eeom function in libbfd.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29 and earlier, allows remote attackers to cause an out of bounds heap read via a crafted vms alpha file.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=21813
