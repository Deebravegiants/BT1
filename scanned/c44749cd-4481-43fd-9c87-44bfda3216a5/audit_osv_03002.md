# [M] ALPINE-CVE-2024-23770

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-23770
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23770
Type: osv

## Affected
- Alpine:v3.20: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.21: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.22: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.23: `darkhttpd` — affected >=0 <1.15-r0
- Alpine:v3.24: `darkhttpd` — affected >=0 <1.15-r0

## Details
darkhttpd through 1.15 allows local users to discover credentials (for --auth) by listing processes and their arguments.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23770
