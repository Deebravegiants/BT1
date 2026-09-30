# [H] ALPINE-CVE-2023-34326

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-34326
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34326
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.5-r3
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r3
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r3
- Alpine:v3.18: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.19: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.20: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.21: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.22: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.23: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.24: `xen` — affected >=0 <4.17.2-r3

## Details
The caching invalidation guidelines from the AMD-Vi specification (48882—Rev
3.07-PUB—Oct 2022) is incorrect on some hardware, as devices will malfunction
(see stale DMA mappings) if some fields of the DTE are updated but the IOMMU
TLB is not flushed.

Such stale DMA mappings can point to memory ranges not owned by the guest, thus
allowing access to unindented memory regions.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-34326
