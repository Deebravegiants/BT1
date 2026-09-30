# [H] ALPINE-CVE-2016-7093

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7093
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7093
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.11: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.12: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.13: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.14: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.15: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.16: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.17: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.18: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.19: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.20: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.21: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.22: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.23: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.24: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r2
- Alpine:v3.5: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.6: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.7: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.8: `xen` — affected >=0 <4.7.0-r1
- Alpine:v3.9: `xen` — affected >=0 <4.7.0-r1

## Details
Xen 4.5.3, 4.6.3, and 4.7.x allow local HVM guest OS administrators to overwrite hypervisor memory and consequently gain host OS privileges by leveraging mishandling of instruction pointer truncation during emulation.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7093
