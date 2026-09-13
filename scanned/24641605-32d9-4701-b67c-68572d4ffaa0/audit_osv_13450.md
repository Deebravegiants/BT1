# [H] CVE-2018-19931

## Summary
Severity: High
Advisory: CVE-2018-19931
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-19931
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils through 2.31. There is a heap-based buffer overflow in bfd_elf32_swap_phdr_in in elfcode.h because the number of program headers is not restricted.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=5f60af5d24d181371d67534fa273dd221df20c07
- http://www.securityfocus.com/bid/106144
- https://security.gentoo.org/glsa/201908-01
- https://usn.ubuntu.com/4336-1/
- https://security.netapp.com/advisory/ntap-20190221-0004/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23942
