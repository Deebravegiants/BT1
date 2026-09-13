# [H] ALPINE-CVE-2019-7638

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-7638
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-7638
Type: osv

## Affected
- Alpine:v3.10: `sdl` — affected >=0 <1.2.15-r11
- Alpine:v3.11: `sdl` — affected >=0 <1.2.15-r11
- Alpine:v3.12: `sdl` — affected >=0 <1.2.15-r11
- Alpine:v3.7: `sdl` — affected >=0 <1.2.15-r8
- Alpine:v3.8: `sdl` — affected >=0 <1.2.15-r9
- Alpine:v3.9: `sdl` — affected >=0 <1.2.15-r10
- Alpine:v3.10: `sdl2` — affected >=0 <2.0.10-r0
- Alpine:v3.11: `sdl2` — affected >=0 <2.0.10-r0
- Alpine:v3.7: `sdl2` — affected >=0 <2.0.10-r0
- Alpine:v3.8: `sdl2` — affected >=0 <2.0.10-r0
- Alpine:v3.9: `sdl2` — affected >=0 <2.0.10-r0

## Details
SDL (Simple DirectMedia Layer) through 1.2.15 and 2.x through 2.0.9 has a heap-based buffer over-read in Map1toN in video/SDL_pixels.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-7638
