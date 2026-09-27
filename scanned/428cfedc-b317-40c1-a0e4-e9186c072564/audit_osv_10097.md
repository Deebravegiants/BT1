# [H] CVE-2017-13710

## Summary
Severity: High
Advisory: CVE-2017-13710
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-27
Source: https://osv.dev/vulnerability/CVE-2017-13710
Type: osv

## Details
The setup_group function in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a group section that is too small.

## References
- http://www.securityfocus.com/bid/100499
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=0c54f69295208331faab9bc5e995111a35672f9b
