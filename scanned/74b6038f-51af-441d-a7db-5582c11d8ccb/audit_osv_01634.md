# [M] ALPINE-CVE-2019-7149

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-7149
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-7149
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
A heap-based buffer over-read was discovered in the function read_srclines in dwarf_getsrclines.c in libdw in elfutils 0.175. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by eu-nm.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-7149
