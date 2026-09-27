# [M] ALPINE-CVE-2022-26362

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-26362
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26362
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r1
- Alpine:v3.14: `xen` — affected >=0 <4.15.2-r1
- Alpine:v3.15: `xen` — affected >=0 <4.15.2-r1
- Alpine:v3.16: `xen` — affected >=0 <4.16.1-r1
- Alpine:v3.17: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.18: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.19: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.20: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.21: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.22: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.23: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.24: `xen` — affected >=0 <4.16.1-r2

## Details
x86 pv: Race condition in typeref acquisition Xen maintains a type reference count for pages, in addition to a regular reference count. This scheme is used to maintain invariants required for Xen's safety, e.g. PV guests may not have direct writeable access to pagetables; updates need auditing by Xen. Unfortunately, the logic for acquiring a type reference has a race condition, whereby a safely TLB flush is issued too early and creates a window where the guest can re-establish the read/write mapping before writeability is prohibited.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26362
