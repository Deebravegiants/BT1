# [H] ALPINE-CVE-2021-28697

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28697
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28697
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.0.0 <4.13.3-r2
- Alpine:v3.12: `xen` — affected >=4.0.0 <4.13.3-r2
- Alpine:v3.13: `xen` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.14: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.15: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.16: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.17: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.18: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.19: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.15.0-r2
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.15.0-r2

## Details
grant table v2 status pages may remain accessible after de-allocation Guest get permitted access to certain Xen-owned pages of memory. The majority of such pages remain allocated / associated with a guest for its entire lifetime. Grant table v2 status pages, however, get de-allocated when a guest switched (back) from v2 to v1. The freeing of such pages requires that the hypervisor know where in the guest these pages were mapped. The hypervisor tracks only one use within guest space, but racing requests from the guest to insert mappings of these pages may result in any of them to become mapped in multiple locations. Upon switching back from v2 to v1, the guest would then retain access to a page that was freed and perhaps re-used for other purposes.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28697
