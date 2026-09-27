# [H] JLSEC-2026-876

## Summary
Severity: High
Advisory: JLSEC-2026-876
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-876
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
ImageMagick before 6.9.11-40 and 7.x before 7.0.10-40 mishandles the -authenticate option, which allows setting a password for password-protected PDF files. The user-controlled password was not properly escaped/sanitized and it was therefore possible to inject additional shell commands via `coders/pdf.c`.

## References
- https://github.com/ImageMagick/ImageMagick/discussions/2851
- https://github.com/ImageMagick/ImageMagick/discussions/2851
- https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html
- https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://security.gentoo.org/glsa/202101-36
- https://security.gentoo.org/glsa/202101-36
