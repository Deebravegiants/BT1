# [C] ALPINE-CVE-2017-6349

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-6349
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6349
Type: osv

## Affected
- Alpine:v3.10: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.11: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.12: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.13: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.14: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.15: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.16: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.17: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.18: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.19: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.20: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.21: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.22: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.23: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.8: `vim` — affected >=0 <8.0.1521-r0
- Alpine:v3.9: `vim` — affected >=0 <8.0.1521-r0

## Details
An integer overflow at a u_read_undo memory allocation site would occur for vim before patch 8.0.0377, if it does not properly validate values for tree length when reading a corrupted undo file, which may lead to resultant buffer overflows.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6349
