# [M] ALPINE-CVE-2023-46842

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46842
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46842
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.16.6-r0
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.16.6-r0
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.17.4-r0
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.18.2-r0
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.18.2-r0
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.18.2-r0
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.18.2-r0
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.18.2-r0
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.18.2-r0

## Details
Unlike 32-bit PV guests, HVM guests may switch freely between 64-bit and
other modes.  This in particular means that they may set registers used
to pass 32-bit-mode hypercall arguments to values outside of the range
32-bit code would be able to set them to.

When processing of hypercalls takes a considerable amount of time,
the hypervisor may choose to invoke a hypercall continuation.  Doing so
involves putting (perhaps updated) hypercall arguments in respective
registers.  For guests not running in 64-bit mode this further involves
a certain amount of translation of the values.

Unfortunately internal sanity checking of these translated values
assumes high halves of registers to always be clear when invoking a
hypercall.  When this is found not to be the case, it triggers a
consistency check in the hypervisor and causes a crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46842
