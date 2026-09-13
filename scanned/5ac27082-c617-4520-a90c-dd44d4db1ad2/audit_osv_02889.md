# [M] ALPINE-CVE-2023-43789

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-43789
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-43789
Type: osv

## Affected
- Alpine:v3.19: `libxpm` — affected >=0 <3.5.17-r0
- Alpine:v3.20: `libxpm` — affected >=0 <3.5.17-r0
- Alpine:v3.21: `libxpm` — affected >=0 <3.5.17-r0
- Alpine:v3.22: `libxpm` — affected >=0 <3.5.17-r0
- Alpine:v3.23: `libxpm` — affected >=0 <3.5.17-r0
- Alpine:v3.24: `libxpm` — affected >=0 <3.5.17-r0

## Details
A vulnerability was found in libXpm where a vulnerability exists due to a boundary condition, a local user can trigger an out-of-bounds read error and read contents of memory on the system.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-43789
