# [M] CVE-2018-10535

## Summary
Severity: Medium
Advisory: CVE-2018-10535
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10535
Type: osv

## Details
The ignore_section_sym function in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, does not validate the output_section pointer in the case of a symtab entry with a "SECTION" type that has a "0" value, which allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted file, as demonstrated by objcopy.

## References
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/104021
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3032
- https://security.gentoo.org/glsa/201908-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=23113
