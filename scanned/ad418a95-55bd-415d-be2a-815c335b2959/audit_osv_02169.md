# [H] ALPINE-CVE-2021-28702

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28702
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28702
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.13.0 <4.13.4-r1
- Alpine:v3.12: `xen` — affected >=4.13.0 <4.13.4-r1
- Alpine:v3.13: `xen` — affected >=4.13.0 <4.14.3-r1
- Alpine:v3.14: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.15: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.16: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.17: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.18: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.19: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.20: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.21: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.22: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.23: `xen` — affected >=4.13.0 <4.15.1-r1
- Alpine:v3.24: `xen` — affected >=4.13.0 <4.15.1-r1

## Details
PCI devices with RMRRs not deassigned correctly Certain PCI devices in a system might be assigned Reserved Memory Regions (specified via Reserved Memory Region Reporting, "RMRR"). These are typically used for platform tasks such as legacy USB emulation. If such a device is passed through to a guest, then on guest shutdown the device is not properly deassigned. The IOMMU configuration for these devices which are not properly deassigned ends up pointing to a freed data structure, including the IO Pagetables. Subsequent DMA or interrupts from the device will have unpredictable behaviour, ranging from IOMMU faults to memory corruption.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28702
