# [M] ALPINE-CVE-2020-29485

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29485
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29485
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.6.0 <4.13.2-r3
- Alpine:v3.12: `xen` — affected >=4.6.0 <4.13.2-r3
- Alpine:v3.13: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=4.6.0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=4.6.0 <4.14.1-r0

## Details
An issue was discovered in Xen 4.6 through 4.14.x. When acting upon a guest XS_RESET_WATCHES request, not all tracking information is freed. A guest can cause unbounded memory usage in oxenstored. This can lead to a system-wide DoS. Only systems using the Ocaml Xenstored implementation are vulnerable. Systems using the C Xenstored implementation are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29485
