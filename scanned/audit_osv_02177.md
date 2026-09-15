# [H] ALPINE-CVE-2021-28710

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28710
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-11-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28710
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.15: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.16: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.17: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.18: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.19: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.20: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.21: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.22: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.23: `xen` — affected >=0 <4.15.1-r1
- Alpine:v3.24: `xen` — affected >=0 <4.15.1-r1

## Details
certain VT-d IOMMUs may not work in shared page table mode For efficiency reasons, address translation control structures (page tables) may (and, on suitable hardware, by default will) be shared between CPUs, for second-level translation (EPT), and IOMMUs. These page tables are presently set up to always be 4 levels deep. However, an IOMMU may require the use of just 3 page table levels. In such a configuration the lop level table needs to be stripped before inserting the root table's address into the hardware pagetable base register. When sharing page tables, Xen erroneously skipped this stripping. Consequently, the guest is able to write to leaf page table entries.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28710
