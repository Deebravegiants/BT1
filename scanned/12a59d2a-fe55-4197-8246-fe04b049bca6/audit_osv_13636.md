# [M] CVE-2018-20651

## Summary
Severity: Medium
Advisory: CVE-2018-20651
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-01
Source: https://osv.dev/vulnerability/CVE-2018-20651
Type: osv

## Details
A NULL pointer dereference was discovered in elf_link_add_object_symbols in elflink.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31.1. This occurs for a crafted ET_DYN with no program headers. A specially crafted ELF file allows remote attackers to cause a denial of service, as demonstrated by ld.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=54025d5812ff100f5f0654eb7e1ffd50f2e37f5f
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/106440
- https://security.gentoo.org/glsa/201908-01
- https://support.f5.com/csp/article/K38336243
- https://sourceware.org/bugzilla/show_bug.cgi?id=24041
