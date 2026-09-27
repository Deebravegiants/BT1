# [H] CVE-2017-17121

## Summary
Severity: High
Advisory: CVE-2017-17121
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-04
Source: https://osv.dev/vulnerability/CVE-2017-17121
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, allows remote attackers to cause a denial of service (memory access violation) or possibly have unspecified other impact via a COFF binary in which a relocation refers to a location after the end of the to-be-relocated section.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=b23dc97fe237a1d9e850d7cbeee066183a00630b
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22506
