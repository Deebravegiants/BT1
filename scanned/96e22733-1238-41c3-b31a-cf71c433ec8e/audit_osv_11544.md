# [H] CVE-2017-8392

## Summary
Severity: High
Advisory: CVE-2017-8392
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8392
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to an invalid read of size 8 because of missing a check to determine whether symbols are NULL in the _bfd_dwarf2_find_nearest_line function. This vulnerability causes programs that conduct an analysis of binary programs using the libbfd library, such as objdump, to crash.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21409
