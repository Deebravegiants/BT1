# [C] ALPINE-CVE-2018-16402

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-16402
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16402
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
libelf/elf_end.c in elfutils 0.173 allows remote attackers to cause a denial of service (double free and application crash) or possibly have unspecified other impact because it tries to decompress twice.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16402
