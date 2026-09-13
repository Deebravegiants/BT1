# [H] CVE-2017-16830

## Summary
Severity: High
Advisory: CVE-2017-16830
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16830
Type: osv

## Details
The print_gnu_property_note function in readelf.c in GNU Binutils 2.29.1 does not have integer-overflow protection on 32-bit platforms, which allows remote attackers to cause a denial of service (segmentation violation and application crash) or possibly have unspecified other impact via a crafted ELF file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=6ab2c4ed51f9c4243691755e1b1d2149c6a426f4
- http://www.securityfocus.com/bid/101941
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22384
