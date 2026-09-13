# [H] CVE-2018-10254

## Summary
Severity: High
Advisory: CVE-2018-10254
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-21
Source: https://osv.dev/vulnerability/CVE-2018-10254
Type: osv

## Details
Netwide Assembler (NASM) 2.13 has a stack-based buffer over-read in the disasm function of the disasm/disasm.c file. Remote attackers could leverage this vulnerability to cause a denial of service or possibly have unspecified other impact via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://sourceforge.net/p/nasm/bugs/561/
