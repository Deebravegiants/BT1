# [M] CVE-2017-14933

## Summary
Severity: Medium
Advisory: CVE-2017-14933
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14933
Type: osv

## Details
read_formatted_entries in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (infinite loop) via a crafted ELF file.

## References
- http://www.securityfocus.com/bid/101203
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=30d0157a2ad64e64e5ff9fcc0dbe78a3e682f573
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=33e0a9a056bd23e923b929a4f2ab049ade0b1c32
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22210
