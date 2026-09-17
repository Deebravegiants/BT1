# [H] ALPINE-CVE-2018-18883

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-18883
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18883
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.11: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.12: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.13: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.14: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.15: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.16: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.17: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.18: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.19: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.20: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.21: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.22: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.23: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.24: `xen` — affected >=4.9.0 <4.11.1-r0
- Alpine:v3.6: `xen` — affected >=4.9.0 <4.8.5-r0
- Alpine:v3.7: `xen` — affected >=4.9.0 <4.9.3-r1
- Alpine:v3.8: `xen` — affected >=4.9.0 <4.10.2-r1
- Alpine:v3.9: `xen` — affected >=4.9.0 <4.11.1-r0

## Details
An issue was discovered in Xen 4.9.x through 4.11.x, on Intel x86 platforms, allowing x86 HVM and PVH guests to cause a host OS denial of service (NULL pointer dereference) or possibly have unspecified other impact because nested VT-x is not properly restricted.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18883
