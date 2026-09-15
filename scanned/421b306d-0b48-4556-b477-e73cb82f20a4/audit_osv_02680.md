# [H] ALPINE-CVE-2022-42327

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42327
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42327
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.18: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.19: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.20: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.21: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.22: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.23: `xen` — affected >=0 <4.16.2-r1
- Alpine:v3.24: `xen` — affected >=0 <4.16.2-r1

## Details
x86: unintended memory sharing between guests On Intel systems that support the "virtualize APIC accesses" feature, a guest can read and write the global shared xAPIC page by moving the local APIC out of xAPIC mode. Access to this shared page bypasses the expected isolation that should exist between two guests.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42327
