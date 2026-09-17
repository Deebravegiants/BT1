# [H] ALPINE-CVE-2017-8903

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8903
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8903
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.11: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.12: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.13: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.14: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.15: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.16: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.17: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.18: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.19: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.20: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.21: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.22: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.23: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.24: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.3: `xen` — affected >=0 <4.6.3-r7
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r9
- Alpine:v3.5: `xen` — affected >=0 <4.7.2-r1
- Alpine:v3.6: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.7: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.8: `xen` — affected >=0 <4.8.1-r2
- Alpine:v3.9: `xen` — affected >=0 <4.8.1-r2

## Details
Xen through 4.8.x on 64-bit platforms mishandles page tables after an IRET hypercall, which might allow PV guest OS users to execute arbitrary code on the host OS, aka XSA-213.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8903
