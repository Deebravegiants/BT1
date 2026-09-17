# [H] CVE-2017-17122

## Summary
Severity: High
Advisory: CVE-2017-17122
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-04
Source: https://osv.dev/vulnerability/CVE-2017-17122
Type: osv

## Details
The dump_relocs_in_section function in objdump.c in GNU Binutils 2.29.1 does not check for reloc count integer overflows, which allows remote attackers to cause a denial of service (excessive memory allocation, or heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted PE file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=d785b7d4b877ed465d04072e17ca19d0f47d840f
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22508
