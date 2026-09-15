# [H] CVE-2017-9042

## Summary
Severity: High
Advisory: CVE-2017-9042
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9042
Type: osv

## Details
readelf.c in GNU Binutils 2017-04-12 has a "cannot be represented in type long" issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=7296a62a2a237f6b1ad8db8c38b090e9f592c8cf
- https://security.gentoo.org/glsa/201709-02
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
