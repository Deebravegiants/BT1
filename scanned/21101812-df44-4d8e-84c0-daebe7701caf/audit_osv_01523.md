# [M] ALPINE-CVE-2019-18424

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-18424
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18424
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.1-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r1

## Details
An issue was discovered in Xen through 4.12.x allowing attackers to gain host OS privileges via DMA in a situation where an untrusted domain has access to a physical device. This occurs because passed through PCI devices may corrupt host memory after deassignment. When a PCI device is assigned to an untrusted domain, it is possible for that domain to program the device to DMA to an arbitrary address. The IOMMU is used to protect the host from malicious DMA by making sure that the device addresses can only target memory assigned to the guest. However, when the guest domain is torn down, or the device is deassigned, the device is assigned back to dom0, thus allowing any in-flight DMA to potentially target critical host data. An untrusted domain with access to a physical device can DMA into host memory, leading to privilege escalation. Only systems where guests are given direct access to physical devices capable of DMA (PCI pass-through) are vulnerable. Systems which do not use PCI pass-through are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18424
