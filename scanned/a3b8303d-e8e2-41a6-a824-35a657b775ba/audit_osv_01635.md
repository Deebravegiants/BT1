# [M] ALPINE-CVE-2019-7150

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-7150
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-7150
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
An issue was discovered in elfutils 0.175. A segmentation fault can occur in the function elf64_xlatetom in libelf/elf32_xlatetom.c, due to dwfl_segment_report_module not checking whether the dyn data read from a core file is truncated. A crafted input can cause a program crash, leading to denial-of-service, as demonstrated by eu-stack.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-7150
