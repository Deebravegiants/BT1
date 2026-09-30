# [M] ALPINE-CVE-2024-2201

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-2201
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-2201
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=0 <4.16.6-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.6-r0
- Alpine:v3.18: `xen` — affected >=0 <4.17.4-r0
- Alpine:v3.19: `xen` — affected >=0 <4.18.2-r0
- Alpine:v3.20: `xen` — affected >=0 <4.18.2-r0
- Alpine:v3.21: `xen` — affected >=0 <4.18.2-r0
- Alpine:v3.22: `xen` — affected >=0 <4.18.2-r0
- Alpine:v3.23: `xen` — affected >=0 <4.18.2-r0
- Alpine:v3.24: `xen` — affected >=0 <4.18.2-r0

## Details
A cross-privilege Spectre v2 vulnerability allows attackers to bypass all deployed mitigations, including the recent Fine(IBT), and to leak arbitrary Linux kernel memory on Intel systems.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-2201
