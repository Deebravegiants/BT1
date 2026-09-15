# [M] CVE-2018-10534

## Summary
Severity: Medium
Advisory: CVE-2018-10534
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10534
Type: osv

## Details
The _bfd_XX_bfd_copy_private_bfd_data_common function in peXXigen.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, processes a negative Data Directory size with an unbounded loop that increases the value of (external_IMAGE_DEBUG_DIRECTORY) *edd so that the address exceeds its own memory region, resulting in an out-of-bounds memory write, as demonstrated by objcopy copying private info with _bfd_pex64_bfd_copy_private_bfd_data_common in pex64igen.c.

## References
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/104025
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3032
- https://security.gentoo.org/glsa/201908-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=23110
