# [H] CVE-2017-9744

## Summary
Severity: High
Advisory: CVE-2017-9744
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9744
Type: osv

## Details
The sh_elf_set_mach_from_flags function in bfd/elf32-sh.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted binary file, as demonstrated by mishandling of this file during "objdump -D" execution.

## References
- http://www.securityfocus.com/bid/99108
- https://sourceware.org/bugzilla/show_bug.cgi?id=21578
