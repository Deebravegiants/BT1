# [M] ALPINE-CVE-2022-23035

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-23035
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23035
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=4.6.0 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=4.6.0 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=4.6.0 <4.15.2-r0
- Alpine:v3.15: `xen` — affected >=4.6.0 <4.15.2-r0
- Alpine:v3.16: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.17: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.18: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.19: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.20: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.21: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.22: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.23: `xen` — affected >=4.6.0 <4.16.1-r0
- Alpine:v3.24: `xen` — affected >=4.6.0 <4.16.1-r0

## Details
Insufficient cleanup of passed-through device IRQs The management of IRQs associated with physical devices exposed to x86 HVM guests involves an iterative operation in particular when cleaning up after the guest's use of the device. In the case where an interrupt is not quiescent yet at the time this cleanup gets invoked, the cleanup attempt may be scheduled to be retried. When multiple interrupts are involved, this scheduling of a retry may get erroneously skipped. At the same time pointers may get cleared (resulting in a de-reference of NULL) and freed (resulting in a use-after-free), while other code would continue to assume them to be valid.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23035
