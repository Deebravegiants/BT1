# [M] ALPINE-CVE-2018-5711

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5711
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5711
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
- Alpine:v3.4: `php5` — affected >=0 <5.6.33-r0
- Alpine:v3.5: `php5` — affected >=0 <5.6.33-r0

## Details
gd_gif_in.c in the GD Graphics Library (aka libgd), as used in PHP before 5.6.33, 7.0.x before 7.0.27, 7.1.x before 7.1.13, and 7.2.x before 7.2.1, has an integer signedness error that leads to an infinite loop via a crafted GIF file, as demonstrated by a call to the imagecreatefromgif or imagecreatefromstring PHP function. This is related to GetCode_ and gdImageCreateFromGifCtx.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5711
