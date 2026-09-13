# [C] ALPINE-CVE-2021-22930

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-22930
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22930
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.22.4-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.4-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.17.4-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.17.4-r0

## Details
Node.js before 16.6.0, 14.17.4, and 12.22.4 is vulnerable to a use after free attack where an attacker might be able to exploit the memory corruption, to change process behavior.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22930
