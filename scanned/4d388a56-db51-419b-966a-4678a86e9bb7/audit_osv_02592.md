# [H] ALPINE-CVE-2022-33745

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-33745
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33745
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r5
- Alpine:v3.14: `xen` — affected >=0 <4.15.3-r2
- Alpine:v3.15: `xen` — affected >=0 <4.15.3-r2
- Alpine:v3.17: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.18: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.19: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.20: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.21: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.22: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.23: `xen` — affected >=0 <4.16.1-r6
- Alpine:v3.24: `xen` — affected >=0 <4.16.1-r6

## Details
insufficient TLB flush for x86 PV guests in shadow mode For migration as well as to work around kernels unaware of L1TF (see XSA-273), PV guests may be run in shadow paging mode. To address XSA-401, code was moved inside a function in Xen. This code movement missed a variable changing meaning / value between old and new code positions. The now wrong use of the variable did lead to a wrong TLB flush condition, omitting flushes where such are necessary.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33745
