# [H] JLSEC-2026-364

## Summary
Severity: High
Advisory: JLSEC-2026-364
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-364
Type: osv

## Affected
- Julia: `SDL2_jll` — affected >=0 <2.0.20+0

## Details
There is a heap overflow problem in `video/SDL_pixels.c` in SDL (Simple DirectMedia Layer) 2.x to 2.0.18 versions. By crafting a malicious .BMP file, an attacker can cause the application using this library to crash, denial of service or Code execution.

## References
- https://github.com/libsdl-org/SDL/commit/8c91cf7dba5193f5ce12d06db1336515851c9ee9
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://security.gentoo.org/glsa/202305-17
- https://security.gentoo.org/glsa/202305-18
