# [H] ALPINE-CVE-2018-19963

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19963
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19963
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.11: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.12: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.13: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.9: `xen` — affected >=0 <4.11.1-r0

## Details
An issue was discovered in Xen 4.11 allowing HVM guest OS users to cause a denial of service (host OS crash) or possibly gain host OS privileges because x86 IOREQ server resource accounting (for external emulators) was mishandled.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19963
