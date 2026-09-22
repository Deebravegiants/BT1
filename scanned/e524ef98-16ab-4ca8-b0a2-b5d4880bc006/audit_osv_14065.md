# [M] CVE-2018-6872

## Summary
Severity: Medium
Advisory: CVE-2018-6872
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-6872
Type: osv

## Details
The elf_parse_notes function in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, allows remote attackers to cause a denial of service (out-of-bounds read and segmentation violation) via a note with a large alignment.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Ba=commit%3Bh=ef135d4314fd4c2d7da66b9d7b59af4a85b0f7e6
- http://www.securityfocus.com/bid/103103
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22788
