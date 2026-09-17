# [M] ALPINE-CVE-2021-3308

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3308
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3308
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.13.1 <4.13.2-r4
- Alpine:v3.12: `xen` — affected >=4.13.1 <4.13.2-r4
- Alpine:v3.13: `xen` — affected >=4.13.1 <4.14.1-r1
- Alpine:v3.14: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.15: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.16: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.17: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.18: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.19: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.20: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.21: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.22: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.23: `xen` — affected >=4.13.1 <4.14.1-r2
- Alpine:v3.24: `xen` — affected >=4.13.1 <4.14.1-r2

## Details
An issue was discovered in Xen 4.12.3 through 4.12.4 and 4.13.1 through 4.14.x. An x86 HVM guest with PCI pass through devices can force the allocation of all IDT vectors on the system by rebooting itself with MSI or MSI-X capabilities enabled and entries setup. Such reboots will leak any vectors used by the MSI(-X) entries that the guest might had enabled, and hence will lead to vector exhaustion on the system, not allowing further PCI pass through devices to work properly. HVM guests with PCI pass through devices can mount a Denial of Service (DoS) attack affecting the pass through of PCI devices to other guests or the hardware domain. In the latter case, this would affect the entire host.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3308
