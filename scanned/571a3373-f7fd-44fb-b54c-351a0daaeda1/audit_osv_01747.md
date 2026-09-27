# [M] ALPINE-CVE-2020-14002

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14002
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14002
Type: osv

## Affected
- Alpine:v3.10: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.11: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.12: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.13: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.14: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.15: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.16: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.17: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.18: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.19: `putty` — affected >=0.68 <0.74-r0
- Alpine:v3.9: `putty` — affected >=0.68 <0.74-r0

## Details
PuTTY 0.68 through 0.73 has an Observable Discrepancy leading to an information leak in the algorithm negotiation. This allows man-in-the-middle attackers to target initial connection attempts (where no host key for the server has been cached by the client).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14002
