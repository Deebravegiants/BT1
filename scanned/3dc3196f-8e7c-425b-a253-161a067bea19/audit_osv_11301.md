# [H] CVE-2017-7302

## Summary
Severity: High
Advisory: CVE-2017-7302
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7302
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, has a swap_std_reloc_out function in bfd/aoutx.h that is vulnerable to an invalid read (of size 4) because of missing checks for relocs that could not be recognised. This vulnerability causes Binutils utilities like strip to crash.

## References
- http://www.securityfocus.com/bid/97216
- https://sourceware.org/bugzilla/show_bug.cgi?id=20921
