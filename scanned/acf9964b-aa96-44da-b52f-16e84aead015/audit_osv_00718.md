# [H] ALPINE-CVE-2017-7228

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7228
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7228
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.11: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.12: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.13: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.14: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.15: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.16: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.17: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.18: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.19: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.20: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.21: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.22: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.23: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.24: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r8
- Alpine:v3.5: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.6: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.7: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.8: `xen` — affected >=0 <4.7.2-r0
- Alpine:v3.9: `xen` — affected >=0 <4.7.2-r0

## Details
An issue (known as XSA-212) was discovered in Xen, with fixes available for 4.8.x, 4.7.x, 4.6.x, 4.5.x, and 4.4.x. The earlier XSA-29 fix introduced an insufficient check on XENMEM_exchange input, allowing the caller to drive hypervisor memory accesses outside of the guest provided input/output arrays.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7228
