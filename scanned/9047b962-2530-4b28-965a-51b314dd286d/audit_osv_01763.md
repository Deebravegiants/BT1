# [M] ALPINE-CVE-2020-14344

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14344
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14344
Type: osv

## Affected
- Alpine:v3.10: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.11: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.12: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.13: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.14: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.15: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.16: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.17: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.18: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.19: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.20: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.21: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.22: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.23: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.24: `libx11` — affected >=0 <1.6.10-r0
- Alpine:v3.9: `libx11` — affected >=0 <1.6.10-r0

## Details
An integer overflow leading to a heap-buffer overflow was found in The X Input Method (XIM) client was implemented in libX11 before version 1.6.10. As per upstream this is security relevant when setuid programs call XIM client functions while running with elevated privileges. No such programs are shipped with Red Hat Enterprise Linux.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14344
