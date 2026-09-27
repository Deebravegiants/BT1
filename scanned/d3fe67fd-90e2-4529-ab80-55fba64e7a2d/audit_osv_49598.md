# [M] CVE-2019-14249

## Summary
Severity: Medium
Advisory: CVE-2019-14249
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-24
Source: https://osv.dev/vulnerability/CVE-2019-14249
Type: osv

## Details
dwarf_elf_load_headers.c in libdwarf before 2019-07-05 allows attackers to cause a denial of service (division by zero) via an ELF file with a zero-size section group (SHT_GROUP), as demonstrated by dwarfdump.

## References
- http://www.securityfocus.com/bid/109380
- https://sourceforge.net/p/libdwarf/code/ci/cb7198abde46c2ae29957ad460da6886eaa606ba/tree/libdwarf/dwarf_elf_load_headers.c?diff=99e77c3894877a1dd80b82808d8309eded4e5599
- https://sourceforge.net/p/libdwarf/code/merge-requests/4/
