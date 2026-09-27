# [M] ALPINE-CVE-2019-7665

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-7665
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-7665
Type: osv

## Affected
- Alpine:v3.12: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.13: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.14: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.15: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.16: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.17: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.18: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.19: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.20: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.21: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.22: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.23: `elfutils` — affected >=0 <0.176-r0
- Alpine:v3.24: `elfutils` — affected >=0 <0.176-r0

## Details
In elfutils 0.175, a heap-based buffer over-read was discovered in the function elf32_xlatetom in elf32_xlatetom.c in libelf. A crafted ELF input can cause a segmentation fault leading to denial of service (program crash) because ebl_core_note does not reject malformed core file notes.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-7665
