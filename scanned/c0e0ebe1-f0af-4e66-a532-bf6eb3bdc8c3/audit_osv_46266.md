# [H] JLSEC-2026-898

## Summary
Severity: High
Advisory: JLSEC-2026-898
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-898
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+3

## Details
A vulnerability was found in ImageMagick, causing an outside the range of representable values of type 'unsigned char' at `coders/psd.c`, when crafted or untrusted input is processed. This leads to a negative impact to application availability or other problems related to undefined behavior.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2091811
- https://bugzilla.redhat.com/show_bug.cgi?id=2091811
- https://github.com/ImageMagick/ImageMagick/commit/9c9a84cec4ab28ee0b57c2b9266d6fbe68183512
- https://github.com/ImageMagick/ImageMagick/commit/9c9a84cec4ab28ee0b57c2b9266d6fbe68183512
- https://github.com/ImageMagick/ImageMagick6/commit/450949ed017f009b399c937cf362f0058eacc5fa
- https://github.com/ImageMagick/ImageMagick6/commit/450949ed017f009b399c937cf362f0058eacc5fa
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
