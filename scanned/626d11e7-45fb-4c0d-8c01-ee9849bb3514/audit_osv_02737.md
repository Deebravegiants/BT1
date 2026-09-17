# [M] ALPINE-CVE-2022-48303

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-48303
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-48303
Type: osv

## Affected
- Alpine:v3.14: `tar` — affected >=0 <1.34-r1
- Alpine:v3.15: `tar` — affected >=0 <1.34-r1
- Alpine:v3.16: `tar` — affected >=0 <1.34-r1
- Alpine:v3.17: `tar` — affected >=0 <1.34-r2
- Alpine:v3.18: `tar` — affected >=0 <1.34-r2
- Alpine:v3.19: `tar` — affected >=0 <1.34-r2
- Alpine:v3.20: `tar` — affected >=0 <1.34-r2
- Alpine:v3.21: `tar` — affected >=0 <1.34-r2
- Alpine:v3.22: `tar` — affected >=0 <1.34-r2
- Alpine:v3.23: `tar` — affected >=0 <1.34-r2
- Alpine:v3.24: `tar` — affected >=0 <1.34-r2

## Details
GNU Tar through 1.34 has a one-byte out-of-bounds read that results in use of uninitialized memory for a conditional jump. Exploitation to change the flow of control has not been demonstrated. The issue occurs in from_header in list.c via a V7 archive in which mtime has approximately 11 whitespace characters.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-48303
