# [H] CVE-2020-14409

## Summary
Severity: High
Advisory: CVE-2020-14409
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-01-19
Source: https://osv.dev/vulnerability/CVE-2020-14409
Type: osv

## Details
SDL (Simple DirectMedia Layer) through 2.0.12 has an Integer Overflow (and resultant SDL_memcpy heap corruption) in SDL_BlitCopy in video/SDL_blit_copy.c via a crafted .BMP file.

## References
- https://lists.debian.org/debian-lts-announce/2021/01/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FS32YCEJLQ2FYUWSWYI2ZMQWQEAWJNR/
- https://security.gentoo.org/glsa/202107-55
- https://www.starwindsoftware.com/security/sw-20210325-0001/
- https://bugzilla.libsdl.org/show_bug.cgi?id=5200
- https://hg.libsdl.org/SDL/rev/3f9b4e92c1d9
