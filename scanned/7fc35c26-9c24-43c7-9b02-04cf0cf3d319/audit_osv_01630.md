# [H] ALPINE-CVE-2019-6977

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6977
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6977
Type: osv

## Affected
- Alpine:v3.10: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.11: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.12: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.13: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.14: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.15: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.16: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.17: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.18: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.19: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.20: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.21: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.22: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.23: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.24: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.6: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.7: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.8: `gd` — affected >=0 <2.2.5-r2
- Alpine:v3.9: `gd` — affected >=0 <2.2.5-r2

## Details
gdImageColorMatch in gd_color_match.c in the GD Graphics Library (aka LibGD) 2.2.5, as used in the imagecolormatch function in PHP before 5.6.40, 7.x before 7.1.26, 7.2.x before 7.2.14, and 7.3.x before 7.3.1, has a heap-based buffer overflow. This can be exploited by an attacker who is able to trigger imagecolormatch calls with crafted image data.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6977
