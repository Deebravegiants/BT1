# [M] ALPINE-CVE-2023-34320

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-34320
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34320
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r3
- Alpine:v3.16: `xen` — affected >=0 <4.16.4-r3
- Alpine:v3.17: `xen` — affected >=0 <4.16.4-r3
- Alpine:v3.18: `xen` — affected >=0 <4.17.1-r4
- Alpine:v3.19: `xen` — affected >=0 <4.17.1-r5
- Alpine:v3.20: `xen` — affected >=0 <4.17.1-r5
- Alpine:v3.21: `xen` — affected >=0 <4.17.1-r5
- Alpine:v3.22: `xen` — affected >=0 <4.17.1-r5
- Alpine:v3.23: `xen` — affected >=0 <4.17.1-r5
- Alpine:v3.24: `xen` — affected >=0 <4.17.1-r5

## Details
Cortex-A77 cores (r0p0 and r1p0) are affected by erratum 1508412
where software, under certain circumstances, could deadlock a core
due to the execution of either a load to device or non-cacheable memory,
and either a store exclusive or register read of the Physical
Address Register (PAR_EL1) in close proximity.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-34320
