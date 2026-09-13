# [M] CVE-2017-9044

## Summary
Severity: Medium
Advisory: CVE-2017-9044
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9044
Type: osv

## Details
The print_symbol_for_build_attribute function in readelf.c in GNU Binutils 2017-04-12 allows remote attackers to cause a denial of service (invalid read and SEGV) via a crafted ELF file.

## References
- http://www.securityfocus.com/bid/98587
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
