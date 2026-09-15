# [M] CVE-2017-15024

## Summary
Severity: Medium
Advisory: CVE-2017-15024
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15024
Type: osv

## Details
find_abstract_instance_name in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (infinite recursion and application crash) via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=52a93b95ec0771c97e26f0bb28630a271a667bd2
- https://blogs.gentoo.org/ago/2017/10/03/binutils-infinite-loop-in-find_abstract_instance_name-dwarf2-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22187
