# [H] ALPINE-CVE-2019-13616

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13616
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13616
Type: osv

## Affected
- Alpine:v3.10: `sdl` — affected >=0 <1.2.15-r12
- Alpine:v3.11: `sdl` — affected >=0 <1.2.15-r12
- Alpine:v3.12: `sdl` — affected >=0 <1.2.15-r12
- Alpine:v3.7: `sdl` — affected >=0 <1.2.15-r9
- Alpine:v3.8: `sdl` — affected >=0 <1.2.15-r10
- Alpine:v3.9: `sdl` — affected >=0 <1.2.15-r11
- Alpine:v3.11: `sdl2_image` — affected >=0 <2.0.5-r1
- Alpine:v3.10: `sdl_image` — affected >=0 <1.2.12-r5
- Alpine:v3.11: `sdl_image` — affected >=0 <1.2.12-r5
- Alpine:v3.7: `sdl_image` — affected >=0 <1.2.12-r4
- Alpine:v3.8: `sdl_image` — affected >=0 <1.2.12-r5
- Alpine:v3.9: `sdl_image` — affected >=0 <1.2.12-r5

## Details
SDL (Simple DirectMedia Layer) through 1.2.15 and 2.x through 2.0.9 has a heap-based buffer over-read in BlitNtoN in video/SDL_blit_N.c when called from SDL_SoftBlit in video/SDL_blit.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13616
