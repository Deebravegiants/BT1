# [H] ALPINE-CVE-2019-18422

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18422
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18422
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.1-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r1

## Details
An issue was discovered in Xen through 4.12.x allowing ARM guest OS users to cause a denial of service or gain privileges by leveraging the erroneous enabling of interrupts. Interrupts are unconditionally unmasked in exception handlers. When an exception occurs on an ARM system which is handled without changing processor level, some interrupts are unconditionally enabled during exception entry. So exceptions which occur when interrupts are masked will effectively unmask the interrupts. A malicious guest might contrive to arrange for critical Xen code to run with interrupts erroneously enabled. This could lead to data corruption, denial of service, or possibly even privilege escalation. However a precise attack technique has not been identified.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18422
