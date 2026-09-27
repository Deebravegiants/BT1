# [M] ALPINE-CVE-2019-5188

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-5188
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5188
Type: osv

## Affected
- Alpine:v3.10: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.11: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.12: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.13: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.14: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.15: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.16: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.17: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.18: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.19: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.20: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.21: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.22: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.23: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.24: `e2fsprogs` — affected >=1.43.3 <1.45.5-r0
- Alpine:v3.8: `e2fsprogs` — affected >=1.43.3 <1.44.2-r2
- Alpine:v3.9: `e2fsprogs` — affected >=1.43.3 <1.44.5-r2

## Details
A code execution vulnerability exists in the directory rehashing functionality of E2fsprogs e2fsck 1.45.4. A specially crafted ext4 directory can cause an out-of-bounds write on the stack, resulting in code execution. An attacker can corrupt a partition to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5188
