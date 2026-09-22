# [M] CVE-2018-20002

## Summary
Severity: Medium
Advisory: CVE-2018-20002
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-20002
Type: osv

## Details
The _bfd_generic_read_minisymbols function in syms.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31, has a memory leak via a crafted ELF file, leading to a denial of service (memory consumption), as demonstrated by nm.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=c2f5dc30afa34696f2da0081c4ac50b958ecb0e9
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/106142
- https://security.gentoo.org/glsa/201908-01
- https://support.f5.com/csp/article/K62602089
- https://sourceware.org/bugzilla/show_bug.cgi?id=23952
- https://security.netapp.com/advisory/ntap-20190221-0004/
