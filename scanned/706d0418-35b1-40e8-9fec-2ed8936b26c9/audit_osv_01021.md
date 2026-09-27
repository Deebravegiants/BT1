# [H] ALPINE-CVE-2018-15911

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-15911
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15911
Type: osv

## Affected
- Alpine:v3.10: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.11: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.12: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.13: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.14: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.15: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.16: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.17: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.18: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.19: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.21: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.22: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.23: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.5: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.6: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.7: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.8: `ghostscript` — affected >=0 <9.24-r0
- Alpine:v3.9: `ghostscript` — affected >=0 <9.24-r0

## Details
In Artifex Ghostscript 9.23 before 2018-08-24, attackers able to supply crafted PostScript could use uninitialized memory access in the aesdecode operator to crash the interpreter or potentially execute code.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15911
