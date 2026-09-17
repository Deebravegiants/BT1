# [M] ALPINE-CVE-2019-14249

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14249
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14249
Type: osv

## Affected
- Alpine:v3.18: `libdwarf` — affected >=0 <0.6.0-r0
- Alpine:v3.19: `libdwarf` — affected >=0 <0.6.0-r0
- Alpine:v3.20: `libdwarf` — affected >=0 <0.6.0-r0
- Alpine:v3.21: `libdwarf` — affected >=0 <0.6.0-r0
- Alpine:v3.22: `libdwarf` — affected >=0 <0.6.0-r0
- Alpine:v3.23: `libdwarf` — affected >=0 <0.6.0-r0
- Alpine:v3.24: `libdwarf` — affected >=0 <0.6.0-r0

## Details
dwarf_elf_load_headers.c in libdwarf before 2019-07-05 allows attackers to cause a denial of service (division by zero) via an ELF file with a zero-size section group (SHT_GROUP), as demonstrated by dwarfdump.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14249
