# [H] CVE-2017-8395

## Summary
Severity: High
Advisory: CVE-2017-8395
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8395
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to an invalid write of size 8 because of missing a malloc() return-value check to see if memory had actually been allocated in the _bfd_generic_get_section_contents function. This vulnerability causes programs that conduct an analysis of binary programs using the libbfd library, such as objcopy, to crash.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21431
