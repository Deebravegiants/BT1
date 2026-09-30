# [H] ALPINE-CVE-2019-12219

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12219
Ecosystem: Alpine:v3.10, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12219
Type: osv

## Affected
- Alpine:v3.10: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.7: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.8: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.9: `sdl2_image` — affected >=0 <2.0.5-r0

## Details
An issue was discovered in libSDL2.a in Simple DirectMedia Layer (SDL) 2.0.9 when used in conjunction with libSDL2_image.a in SDL2_image 2.0.4. There is an invalid free error in the SDL function SDL_SetError_REAL at SDL_error.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12219
