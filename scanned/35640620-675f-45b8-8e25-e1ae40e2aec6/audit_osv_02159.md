# [H] ALPINE-CVE-2021-28692

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28692
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28692
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=3.2.0 <4.13.3-r1
- Alpine:v3.12: `xen` — affected >=3.2.0 <4.13.3-r1
- Alpine:v3.13: `xen` — affected >=3.2.0 <4.14.1-r3
- Alpine:v3.14: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.15.0-r1
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.15.0-r1

## Details
inappropriate x86 IOMMU timeout detection / handling IOMMUs process commands issued to them in parallel with the operation of the CPU(s) issuing such commands. In the current implementation in Xen, asynchronous notification of the completion of such commands is not used. Instead, the issuing CPU spin-waits for the completion of the most recently issued command(s). Some of these waiting loops try to apply a timeout to fail overly-slow commands. The course of action upon a perceived timeout actually being detected is inappropriate: - on Intel hardware guests which did not originally cause the timeout may be marked as crashed, - on AMD hardware higher layer callers would not be notified of the issue, making them continue as if the IOMMU operation succeeded.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28692
