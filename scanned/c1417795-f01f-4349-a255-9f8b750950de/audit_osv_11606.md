# [H] CVE-2017-9043

## Summary
Severity: High
Advisory: CVE-2017-9043
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9043
Type: osv

## Details
readelf.c in GNU Binutils 2017-04-12 has a "shift exponent too large for type unsigned long" issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- http://www.securityfocus.com/bid/98591
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=ddef72cdc10d82ba011a7ff81cafbbd3466acf54
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
