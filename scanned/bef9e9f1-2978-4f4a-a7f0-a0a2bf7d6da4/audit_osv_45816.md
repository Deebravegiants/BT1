# [H] JLSEC-2026-362

## Summary
Severity: High
Advisory: JLSEC-2026-362
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-362
Type: osv

## Affected
- Julia: `SDL2_jll` — affected >=2.0.12+0 <2.24.2+0

## Details
SDL (Simple DirectMedia Layer) through 2.0.12 has an Integer Overflow (and resultant `SDL_memcpy` heap corruption) in `SDL_BlitCopy` in `video/SDL_blit_copy.c` via a crafted .BMP file.

## References
- https://bugzilla.libsdl.org/show_bug.cgi?id=5200
- https://hg.libsdl.org/SDL/rev/3f9b4e92c1d9
- https://lists.debian.org/debian-lts-announce/2021/01/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FS32YCEJLQ2FYUWSWYI2ZMQWQEAWJNR/
- https://security.gentoo.org/glsa/202107-55
- https://www.starwindsoftware.com/security/sw-20210325-0001/
