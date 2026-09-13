# [M] CVE-2017-9039

## Summary
Severity: Medium
Advisory: CVE-2017-9039
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9039
Type: osv

## Details
GNU Binutils 2.28 allows remote attackers to cause a denial of service (memory consumption) via a crafted ELF file with many program headers, related to the get_program_headers function in readelf.c.

## References
- http://www.securityfocus.com/bid/98580
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=82156ab704b08b124d319c0decdbd48b3ca2dac5
- https://security.gentoo.org/glsa/201709-02
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
