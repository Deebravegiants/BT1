# [M] CVE-2020-14410

## Summary
Severity: Medium
Advisory: CVE-2020-14410
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2021-01-19
Source: https://osv.dev/vulnerability/CVE-2020-14410
Type: osv

## Details
SDL (Simple DirectMedia Layer) through 2.0.12 has a heap-based buffer over-read in Blit_3or4_to_3or4__inversed_rgb in video/SDL_blit_N.c via a crafted .BMP file.

## References
- https://lists.debian.org/debian-lts-announce/2021/01/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FS32YCEJLQ2FYUWSWYI2ZMQWQEAWJNR/
- https://security.gentoo.org/glsa/202107-55
- https://bugzilla.libsdl.org/show_bug.cgi?id=5200
- https://hg.libsdl.org/SDL/rev/3f9b4e92c1d9
