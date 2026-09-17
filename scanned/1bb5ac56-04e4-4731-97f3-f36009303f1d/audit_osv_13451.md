# [M] CVE-2018-19932

## Summary
Severity: Medium
Advisory: CVE-2018-19932
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-19932
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils through 2.31. There is an integer overflow and infinite loop caused by the IS_CONTAINED_BY_LMA macro in elf.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=beab453223769279cc1cef68a1622ab8978641f7
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/106144
- https://security.gentoo.org/glsa/201908-01
- https://security.netapp.com/advisory/ntap-20190221-0004/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23932
