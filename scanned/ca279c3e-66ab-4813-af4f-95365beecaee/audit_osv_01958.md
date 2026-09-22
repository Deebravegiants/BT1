# [M] ALPINE-CVE-2020-29571

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29571
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29571
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.4.0 <4.13.2-r3
- Alpine:v3.12: `xen` — affected >=4.4.0 <4.13.2-r3
- Alpine:v3.13: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=4.4.0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=4.4.0 <4.14.1-r0

## Details
An issue was discovered in Xen through 4.14.x. A bounds check common to most operation time functions specific to FIFO event channels depends on the CPU observing consistent state. While the producer side uses appropriately ordered writes, the consumer side isn't protected against re-ordered reads, and may hence end up de-referencing a NULL pointer. Malicious or buggy guest kernels can mount a Denial of Service (DoS) attack affecting the entire system. Only Arm systems may be vulnerable. Whether a system is vulnerable depends on the specific CPU. x86 systems are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29571
