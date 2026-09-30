# [M] CVE-2017-9040

## Summary
Severity: Medium
Advisory: CVE-2017-9040
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9040
Type: osv

## Details
GNU Binutils 2017-04-03 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash), related to the process_mips_specific function in readelf.c, via a crafted ELF file that triggers a large memory-allocation attempt.

## References
- http://www.securityfocus.com/bid/98579
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=7296a62a2a237f6b1ad8db8c38b090e9f592c8cf
- https://security.gentoo.org/glsa/201709-02
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
