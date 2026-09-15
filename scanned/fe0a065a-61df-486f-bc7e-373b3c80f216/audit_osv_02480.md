# [H] ALPINE-CVE-2022-26361

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-26361
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26361
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=0 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=0 <4.15.2-r2
- Alpine:v3.15: `xen` — affected >=0 <4.15.2-r2
- Alpine:v3.16: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.16.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.16.1-r0

## Details
IOMMU: RMRR (VT-d) and unity map (AMD-Vi) handling issues T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Certain PCI devices in a system might be assigned Reserved Memory Regions (specified via Reserved Memory Region Reporting, "RMRR") for Intel VT-d or Unity Mapping ranges for AMD-Vi. These are typically used for platform tasks such as legacy USB emulation. Since the precise purpose of these regions is unknown, once a device associated with such a region is active, the mappings of these regions need to remain continuouly accessible by the device. This requirement has been violated. Subsequent DMA or interrupts from the device may have unpredictable behaviour, ranging from IOMMU faults to memory corruption.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26361
