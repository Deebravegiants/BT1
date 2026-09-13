# [M] ALPINE-CVE-2022-33748

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-33748
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33748
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=4.0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=4.0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=4.0 <4.16.3-r0
- Alpine:v3.17: `xen` — affected >=4.0 <4.16.3-r0
- Alpine:v3.18: `xen` — affected >=4.0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=4.0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=4.0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=4.0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=4.0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=4.0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=4.0 <4.17.0-r0

## Details
lock order inversion in transitive grant copy handling As part of XSA-226 a missing cleanup call was inserted on an error handling path. While doing so, locking requirements were not paid attention to. As a result two cooperating guests granting each other transitive grants can cause locks to be acquired nested within one another, but in respectively opposite order. With suitable timing between the involved grant copy operations this may result in the locking up of a CPU.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33748
