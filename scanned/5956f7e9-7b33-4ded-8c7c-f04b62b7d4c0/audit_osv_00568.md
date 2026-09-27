# [M] ALPINE-CVE-2017-16611

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-16611
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16611
Type: osv

## Affected
- Alpine:v3.10: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.11: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.12: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.13: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.14: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.15: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.16: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.17: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.7: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.8: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.9: `libxfont` — affected >=1.0.0 <1.5.4-r0
- Alpine:v3.10: `libxfont2` — affected >=0 <2.0.3-r0
- Alpine:v3.11: `libxfont2` — affected >=0 <2.0.3-r0
- Alpine:v3.12: `libxfont2` — affected >=0 <2.0.3-r0
- Alpine:v3.7: `libxfont2` — affected >=0 <2.0.3-r0
- Alpine:v3.8: `libxfont2` — affected >=0 <2.0.3-r0
- Alpine:v3.9: `libxfont2` — affected >=0 <2.0.3-r0

## Details
In libXfont before 1.5.4 and libXfont2 before 2.0.3, a local attacker can open (but not read) files on the system as root, triggering tape rewinds, watchdogs, or similar mechanisms that can be triggered by opening files.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16611
