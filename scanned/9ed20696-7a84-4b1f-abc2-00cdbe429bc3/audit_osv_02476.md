# [H] ALPINE-CVE-2022-26357

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-26357
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26357
Type: osv

## Affected
- Alpine:v3.12: `xen` — affected >=4.11.0 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=4.11.0 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=4.11.0 <4.15.2-r2
- Alpine:v3.15: `xen` — affected >=4.11.0 <4.15.2-r2
- Alpine:v3.16: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.17: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.18: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.19: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.20: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.21: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.22: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.23: `xen` — affected >=4.11.0 <4.16.1-r0
- Alpine:v3.24: `xen` — affected >=4.11.0 <4.16.1-r0

## Details
race in VT-d domain ID cleanup Xen domain IDs are up to 15 bits wide. VT-d hardware may allow for only less than 15 bits to hold a domain ID associating a physical device with a particular domain. Therefore internally Xen domain IDs are mapped to the smaller value range. The cleaning up of the housekeeping structures has a race, allowing for VT-d domain IDs to be leaked and flushes to be bypassed.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26357
