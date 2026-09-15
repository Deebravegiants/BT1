# [H] ALPINE-CVE-2020-15565

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15565
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15565
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=3.2.0 <4.12.3-r2
- Alpine:v3.11: `xen` — affected >=3.2.0 <4.13.1-r2
- Alpine:v3.12: `xen` — affected >=3.2.0 <4.13.1-r2
- Alpine:v3.13: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.14: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.13.1-r4
- Alpine:v3.9: `xen` — affected >=3.2.0 <4.11.4-r0

## Details
An issue was discovered in Xen through 4.13.x, allowing x86 Intel HVM guest OS users to cause a host OS denial of service or possibly gain privileges because of insufficient cache write-back under VT-d. When page tables are shared between IOMMU and CPU, changes to them require flushing of both TLBs. Furthermore, IOMMUs may be non-coherent, and hence prior to flushing IOMMU TLBs, a CPU cache also needs writing back to memory after changes were made. Such writing back of cached data was missing in particular when splitting large page mappings into smaller granularity ones. A malicious guest may be able to retain read/write DMA access to frames returned to Xen's free pool, and later reused for another purpose. Host crashes (leading to a Denial of Service) and privilege escalation cannot be ruled out. Xen versions from at least 3.2 onwards are affected. Only x86 Intel systems are affected. x86 AMD as well as Arm systems are not affected. Only x86 HVM guests using hardware assisted paging (HAP), having a passed through PCI device assigned, and having page table sharing enabled can leverage the vulnerability. Note that page table sharing will be enabled (by default) only if Xen considers IOMMU and CPU large page size support compatible.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15565
