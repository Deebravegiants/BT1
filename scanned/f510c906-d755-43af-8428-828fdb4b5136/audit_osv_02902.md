# [M] ALPINE-CVE-2023-46835

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46835
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46835
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.5-r3
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r4
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r4
- Alpine:v3.18: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.19: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.20: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.21: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.22: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.23: `xen` — affected >=0 <4.17.2-r4
- Alpine:v3.24: `xen` — affected >=0 <4.17.2-r4

## Details
The current setup of the quarantine page tables assumes that the
quarantine domain (dom_io) has been initialized with an address width
of DEFAULT_DOMAIN_ADDRESS_WIDTH (48) and hence 4 page table levels.

However dom_io being a PV domain gets the AMD-Vi IOMMU page tables
levels based on the maximum (hot pluggable) RAM address, and hence on
systems with no RAM above the 512GB mark only 3 page-table levels are
configured in the IOMMU.

On systems without RAM above the 512GB boundary
amd_iommu_quarantine_init() will setup page tables for the scratch
page with 4 levels, while the IOMMU will be configured to use 3 levels
only, resulting in the last page table directory (PDE) effectively
becoming a page table entry (PTE), and hence a device in quarantine
mode gaining write access to the page destined to be a PDE.

Due to this page table level mismatch, the sink page the device gets
read/write access to is no longer cleared between device assignment,
possibly leading to data leaks.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46835
