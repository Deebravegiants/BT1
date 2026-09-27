# [H] JLSEC-2026-913

## Summary
Severity: High
Advisory: JLSEC-2026-913
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-913
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=7.1.0+0 <7.1.1047+0

## Details
ImageMagick is a free and open-source software suite, used for editing and manipulating digital images. The `AppImage` version `ImageMagick` might use an empty path when setting `MAGICK_CONFIGURE_PATH` and `LD_LIBRARY_PATH` environment variables while executing, which might lead to arbitrary code execution by loading malicious configuration files or shared libraries in the current working directory while executing `ImageMagick`. The vulnerability is fixed in 7.11-36.

## References
- https://github.com/ImageMagick/ImageMagick/blob/3b22378a23d59d7517c43b65b1822f023df357a0/app-image/AppRun#L11-L14
- https://github.com/ImageMagick/ImageMagick/commit/6526a2b28510ead6a3e14de711bb991ad9abff38
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8rxc-922v-phg8
