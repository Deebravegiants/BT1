# [H] ALPINE-CVE-2016-6258

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6258
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6258
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.11: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r1
- Alpine:v3.5: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.6: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.7: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.7.0-r0
- Alpine:v3.9: `xen` — affected >=0 <4.7.0-r0

## Details
The PV pagetable code in arch/x86/mm.c in Xen 4.7.x and earlier allows local 32-bit PV guest OS administrators to gain host OS privileges by leveraging fast-paths for updating pagetable entries.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6258
