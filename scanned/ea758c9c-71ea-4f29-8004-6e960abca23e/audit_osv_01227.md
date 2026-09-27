# [M] ALPINE-CVE-2018-6872

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-6872
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6872
Type: osv

## Affected
- Alpine:v3.7: `binutils` — affected >=0 <2.30-r2
- Alpine:v3.8: `binutils` — affected >=0 <2.30-r6

## Details
The elf_parse_notes function in elf.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, allows remote attackers to cause a denial of service (out-of-bounds read and segmentation violation) via a note with a large alignment.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6872
