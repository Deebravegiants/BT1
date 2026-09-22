# [H] CVE-2021-33657

## Summary
Severity: High
Advisory: CVE-2021-33657
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-01
Source: https://osv.dev/vulnerability/CVE-2021-33657
Type: osv

## Details
There is a heap overflow problem in video/SDL_pixels.c in SDL (Simple DirectMedia Layer) 2.x to 2.0.18 versions. By crafting a malicious .BMP file, an attacker can cause the application using this library to crash, denial of service or Code execution.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://security.gentoo.org/glsa/202305-17
- https://security.gentoo.org/glsa/202305-18
- https://github.com/libsdl-org/SDL/commit/8c91cf7dba5193f5ce12d06db1336515851c9ee9
