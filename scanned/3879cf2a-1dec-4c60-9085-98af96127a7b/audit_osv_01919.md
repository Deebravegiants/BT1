# [H] ALPINE-CVE-2020-27671

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-27671
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27671
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.2.0 <4.12.4-r0
- Alpine:v3.11: `xen` — affected >=4.2.0 <4.13.2-r0
- Alpine:v3.12: `xen` — affected >=4.2.0 <4.13.2-r0
- Alpine:v3.13: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.14: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.15: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.16: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.17: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.18: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.19: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.20: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.21: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.22: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.23: `xen` — affected >=4.2.0 <4.14.0-r2
- Alpine:v3.24: `xen` — affected >=4.2.0 <4.14.0-r2

## Details
An issue was discovered in Xen through 4.14.x allowing x86 HVM and PVH guest OS users to cause a denial of service (data corruption), cause a data leak, or possibly gain privileges because coalescing of per-page IOMMU TLB flushes is mishandled.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27671
