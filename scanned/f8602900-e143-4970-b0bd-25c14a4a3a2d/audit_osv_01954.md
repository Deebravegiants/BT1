# [M] ALPINE-CVE-2020-29567

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29567
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29567
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.14.1-r0

## Details
An issue was discovered in Xen 4.14.x. When moving IRQs between CPUs to distribute the load of IRQ handling, IRQ vectors are dynamically allocated and de-allocated on the relevant CPUs. De-allocation has to happen when certain constraints are met. If these conditions are not met when first checked, the checking CPU may send an interrupt to itself, in the expectation that this IRQ will be delivered only after the condition preventing the cleanup has cleared. For two specific IRQ vectors, this expectation was violated, resulting in a continuous stream of self-interrupts, which renders the CPU effectively unusable. A domain with a passed through PCI device can cause lockup of a physical CPU, resulting in a Denial of Service (DoS) to the entire host. Only x86 systems are vulnerable. Arm systems are not vulnerable. Only guests with physical PCI devices passed through to them can exploit the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29567
