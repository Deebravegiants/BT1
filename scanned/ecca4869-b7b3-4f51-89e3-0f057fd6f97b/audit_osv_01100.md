# [M] ALPINE-CVE-2018-19964

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-19964
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19964
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.11: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.12: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.13: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.14: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.15: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.16: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.17: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.18: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.19: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.20: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.21: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.22: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.23: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.24: `xen` — affected >=4.11.0 <4.11.1-r0
- Alpine:v3.9: `xen` — affected >=4.11.0 <4.11.1-r0

## Details
An issue was discovered in Xen 4.11.x allowing x86 guest OS users to cause a denial of service (host OS hang) because the p2m lock remains unavailable indefinitely in certain error conditions.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19964
