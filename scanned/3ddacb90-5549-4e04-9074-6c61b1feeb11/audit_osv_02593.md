# [M] ALPINE-CVE-2022-33746

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-33746
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33746
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=4.13.0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=4.13.0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=4.13.0 <4.16.3-r0
- Alpine:v3.17: `xen` — affected >=4.13.0 <4.16.3-r0
- Alpine:v3.18: `xen` — affected >=4.13.0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=4.13.0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=4.13.0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=4.13.0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=4.13.0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=4.13.0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=4.13.0 <4.17.0-r0

## Details
P2M pool freeing may take excessively long The P2M pool backing second level address translation for guests may be of significant size. Therefore its freeing may take more time than is reasonable without intermediate preemption checks. Such checking for the need to preempt was so far missing.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33746
