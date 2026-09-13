# [H] CVE-2017-17126

## Summary
Severity: High
Advisory: CVE-2017-17126
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-04
Source: https://osv.dev/vulnerability/CVE-2017-17126
Type: osv

## Details
The load_debug_section function in readelf.c in GNU Binutils 2.29.1 allows remote attackers to cause a denial of service (invalid memory access and application crash) or possibly have unspecified other impact via an ELF file that lacks section headers.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=f425ec6600b69e39eb605f3128806ff688137ea8
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22510
