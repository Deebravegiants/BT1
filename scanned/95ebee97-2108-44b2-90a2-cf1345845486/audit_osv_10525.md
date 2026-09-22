# [H] CVE-2017-16831

## Summary
Severity: High
Advisory: CVE-2017-16831
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16831
Type: osv

## Details
coffgen.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, does not validate the symbol count, which allows remote attackers to cause a denial of service (integer overflow and application crash, or excessive memory allocation) or possibly have unspecified other impact via a crafted PE file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=6cee897971d4d7cd37d2a686bb6d2aa3e759c8ca
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22385
