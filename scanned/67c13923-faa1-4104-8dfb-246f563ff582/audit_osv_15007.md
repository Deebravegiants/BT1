# [M] CVE-2019-12972

## Summary
Severity: Medium
Advisory: CVE-2019-12972
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12972
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32. There is a heap-based buffer over-read in _bfd_doprnt in bfd.c because elf_object_p in elfcode.h mishandles an e_shstrndx section of type SHT_GROUP by omitting a trailing '\0' character.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=890f750a3b053532a4b839a2dd6243076de12031
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- http://www.securityfocus.com/bid/108903
- https://security.gentoo.org/glsa/202007-39
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24689
