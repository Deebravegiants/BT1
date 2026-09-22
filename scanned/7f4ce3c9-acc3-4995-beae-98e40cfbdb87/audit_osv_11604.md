# [M] CVE-2017-9041

## Summary
Severity: Medium
Advisory: CVE-2017-9041
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9041
Type: osv

## Details
GNU Binutils 2.28 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file, related to MIPS GOT mishandling in the process_mips_specific function in readelf.c.

## References
- http://www.securityfocus.com/bid/98598
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=75ec1fdbb797a389e4fe4aaf2e15358a070dcc19
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=c4ab9505b53cdc899506ed421fddb7e1f8faf7a3
- https://security.gentoo.org/glsa/201709-02
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
