# [H] ALPINE-CVE-2019-5094

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-5094
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5094
Type: osv

## Affected
- Alpine:v3.10: `e2fsprogs` — affected >=1.43.3 <1.45.2-r1
- Alpine:v3.11: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.12: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.13: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.14: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.15: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.16: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.17: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.18: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.19: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.20: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.21: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.22: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.23: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.24: `e2fsprogs` — affected >=1.43.3 <1.45.4-r0
- Alpine:v3.7: `e2fsprogs` — affected >=1.43.3 <1.43.7-r1
- Alpine:v3.8: `e2fsprogs` — affected >=1.43.3 <1.44.2-r1
- Alpine:v3.9: `e2fsprogs` — affected >=1.43.3 <1.44.5-r1

## Details
An exploitable code execution vulnerability exists in the quota file functionality of E2fsprogs 1.45.3. A specially crafted ext4 partition can cause an out-of-bounds write on the heap, resulting in code execution. An attacker can corrupt a partition to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5094
