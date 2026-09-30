# [H] ALPINE-CVE-2023-52425

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-52425
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-52425
Type: osv

## Affected
- Alpine:v3.16: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.17: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.18: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.19: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.20: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.21: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.22: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.23: `expat` — affected >=0 <2.6.0-r0
- Alpine:v3.24: `expat` — affected >=0 <2.6.0-r0

## Details
libexpat through 2.5.0 allows a denial of service (resource consumption) because many full reparsings are required in the case of a large token for which multiple buffer fills are needed.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-52425
