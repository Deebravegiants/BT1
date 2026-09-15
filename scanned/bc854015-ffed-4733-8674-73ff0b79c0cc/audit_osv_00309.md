# [C] ALPINE-CVE-2016-9603

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-9603
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9603
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.11: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.12: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.13: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.14: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.15: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.16: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.17: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.18: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.19: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.20: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.21: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.22: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.23: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.24: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r8
- Alpine:v3.5: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.6: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.7: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.8: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.9: `xen` — affected >=0 <4.7.2-r0

## Details
A heap buffer overflow flaw was found in QEMU's Cirrus CLGD 54xx VGA emulator's VNC display driver support before 2.9; the issue could occur when a VNC client attempted to update its display after a VGA operation is performed by a guest. A privileged user/process inside a guest could use this flaw to crash the QEMU process or, potentially, execute arbitrary code on the host with privileges of the QEMU process.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9603
