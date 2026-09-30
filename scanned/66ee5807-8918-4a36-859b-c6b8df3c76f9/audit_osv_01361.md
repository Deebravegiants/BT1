# [M] ALPINE-CVE-2019-12218

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12218
Ecosystem: Alpine:v3.10, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12218
Type: osv

## Affected
- Alpine:v3.10: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.7: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.8: `sdl2_image` — affected >=0 <2.0.5-r0
- Alpine:v3.9: `sdl2_image` — affected >=0 <2.0.5-r0

## Details
An issue was discovered in libSDL2.a in Simple DirectMedia Layer (SDL) 2.0.9 when used in conjunction with libSDL2_image.a in SDL2_image 2.0.4. There is a NULL pointer dereference in the SDL2_image function IMG_LoadPCX_RW at IMG_pcx.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12218
