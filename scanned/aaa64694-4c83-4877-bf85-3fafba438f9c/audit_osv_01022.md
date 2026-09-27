# [M] ALPINE-CVE-2018-16062

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-16062
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16062
Type: osv

## Affected
- Alpine:v3.12: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.13: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.14: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.15: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.16: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.17: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.18: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.19: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.20: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.21: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.22: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.23: `elfutils` — affected >=0 <0.174-r0
- Alpine:v3.24: `elfutils` — affected >=0 <0.174-r0

## Details
dwarf_getaranges in dwarf_getaranges.c in libdw in elfutils before 2018-08-18 allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16062
