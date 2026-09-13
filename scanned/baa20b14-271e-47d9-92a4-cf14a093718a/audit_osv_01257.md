# [M] ALPINE-CVE-2018-7570

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-7570
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7570
Type: osv

## Affected
- Alpine:v3.7: `binutils` — affected >=0 <2.30-r2
- Alpine:v3.8: `binutils` — affected >=0 <2.30-r6

## Details
The assign_file_positions_for_non_load_sections function in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via an ELF file with a RELRO segment that lacks a matching LOAD segment, as demonstrated by objcopy.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7570
