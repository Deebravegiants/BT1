# [H] CVE-2018-16981

## Summary
Severity: High
Advisory: CVE-2018-16981
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-16981
Type: osv

## Details
stb stb_image.h 2.19, as used in catimg, Emscripten, and other products, has a heap-based buffer overflow in the stbi__out_gif_code function.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00045.html
- https://github.com/nothings/stb/issues/656
