# [M] CVE-2018-18607

## Summary
Severity: Medium
Advisory: CVE-2018-18607
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/CVE-2018-18607
Type: osv

## Details
An issue was discovered in elf_link_input_bfd in elflink.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31. There is a NULL pointer dereference in elf_link_input_bfd when used for finding STT_TLS symbols without any TLS section. A specially crafted ELF allows remote attackers to cause a denial of service, as demonstrated by ld.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=102def4da826b3d9e169741421e5e67e8731909a
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/105754
- https://security.netapp.com/advisory/ntap-20190307-0003/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23805
