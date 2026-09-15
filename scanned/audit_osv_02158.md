# [M] ALPINE-CVE-2021-28690

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28690
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28690
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.12 <4.13.3-r1
- Alpine:v3.12: `xen` — affected >=4.12 <4.13.3-r1
- Alpine:v3.13: `xen` — affected >=4.12 <4.14.1-r3
- Alpine:v3.14: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.15: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.16: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.17: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.18: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.19: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.20: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.21: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.22: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.23: `xen` — affected >=4.12 <4.15.0-r1
- Alpine:v3.24: `xen` — affected >=4.12 <4.15.0-r1

## Details
x86: TSX Async Abort protections not restored after S3 This issue relates to the TSX Async Abort speculative security vulnerability. Please see https://xenbits.xen.org/xsa/advisory-305.html for details. Mitigating TAA by disabling TSX (the default and preferred option) requires selecting a non-default setting in MSR_TSX_CTRL. This setting isn't restored after S3 suspend.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28690
