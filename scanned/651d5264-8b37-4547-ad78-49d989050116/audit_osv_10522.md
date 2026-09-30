# [H] CVE-2017-16828

## Summary
Severity: High
Advisory: CVE-2017-16828
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16828
Type: osv

## Details
The display_debug_frames function in dwarf.c in GNU Binutils 2.29.1 allows remote attackers to cause a denial of service (integer overflow and heap-based buffer over-read, and application crash) or possibly have unspecified other impact via a crafted ELF file, related to print_debug_frame.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=bf59c5d5f4f5b8b4da1f5f605cfa546f8029b43d
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22386
