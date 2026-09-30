# [H] CVE-2018-6323

## Summary
Severity: High
Advisory: CVE-2018-6323
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2018-6323
Type: osv

## Details
The elf_object_p function in elfcode.h in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, has an unsigned integer overflow because bfd_size_type multiplication is not used. A crafted ELF file allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- http://www.securityfocus.com/bid/102821
- https://sourceware.org/bugzilla/show_bug.cgi?id=22746
- https://www.exploit-db.com/exploits/44035/
