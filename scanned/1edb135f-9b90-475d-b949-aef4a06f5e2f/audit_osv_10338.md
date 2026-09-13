# [M] CVE-2017-15023

## Summary
Severity: Medium
Advisory: CVE-2017-15023
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15023
Type: osv

## Details
read_formatted_entries in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, does not properly validate the format count, which allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted ELF file, related to concat_filename.

## References
- http://www.securityfocus.com/bid/101611
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=c361faae8d964db951b7100cada4dcdc983df1bf
- https://security.gentoo.org/glsa/201801-01
- https://blogs.gentoo.org/ago/2017/10/03/binutils-null-pointer-dereference-in-concat_filename-dwarf2-c/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22200
