# [M] CVE-2018-13033

## Summary
Severity: Medium
Advisory: CVE-2018-13033
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-01
Source: https://osv.dev/vulnerability/CVE-2018-13033
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, allows remote attackers to cause a denial of service (excessive memory allocation and application crash) via a crafted ELF file, as demonstrated by _bfd_elf_parse_attributes in elf-attrs.c and bfd_malloc in libbfd.c. This can occur during execution of nm.

## References
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/104584
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3032
- https://security.gentoo.org/glsa/201908-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=23361
