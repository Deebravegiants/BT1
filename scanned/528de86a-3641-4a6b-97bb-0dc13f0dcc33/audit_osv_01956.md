# [H] ALPINE-CVE-2020-29569

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-29569
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29569
Type: osv

## Affected
- Alpine:v3.13: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.14: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.15: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.16: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.17: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.18: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.19: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.20: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.21: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.22: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.23: `linux-lts` — affected >=0 <5.10.4-r0
- Alpine:v3.24: `linux-lts` — affected >=0 <5.10.4-r0

## Details
An issue was discovered in the Linux kernel through 5.10.1, as used with Xen through 4.14.x. The Linux kernel PV block backend expects the kernel thread handler to reset ring->xenblkd to NULL when stopped. However, the handler may not have time to run if the frontend quickly toggles between the states connect and disconnect. As a consequence, the block backend may re-use a pointer after it was freed. A misbehaving guest can trigger a dom0 crash by continuously connecting / disconnecting a block frontend. Privilege escalation and information leaks cannot be ruled out. This only affects systems with a Linux blkback.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29569
