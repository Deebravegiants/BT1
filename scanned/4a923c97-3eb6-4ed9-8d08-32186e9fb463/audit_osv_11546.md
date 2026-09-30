# [H] CVE-2017-8394

## Summary
Severity: High
Advisory: CVE-2017-8394
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8394
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to an invalid read of size 4 due to NULL pointer dereferencing of _bfd_elf_large_com_section. This vulnerability causes programs that conduct an analysis of binary programs using the libbfd library, such as objcopy, to crash.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21414
