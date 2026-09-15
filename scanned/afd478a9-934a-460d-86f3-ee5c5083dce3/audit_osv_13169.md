# [M] CVE-2018-18309

## Summary
Severity: Medium
Advisory: CVE-2018-18309
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/CVE-2018-18309
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31. An invalid memory address dereference was discovered in read_reloc in reloc.c. The vulnerability causes a segmentation fault and application crash, which leads to denial of service, as demonstrated by objdump, because of missing _bfd_clear_contents bounds checking.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=0930cb3021b8078b34cf216e79eb8608d017864f
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/105692
- https://sourceware.org/bugzilla/show_bug.cgi?id=23770
