# [H] CVE-2019-13298

## Summary
Severity: High
Advisory: CVE-2019-13298
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13298
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has a heap-based buffer overflow at MagickCore/pixel-accessor.h in SetPixelViaPixelInfo because of a MagickCore/enhance.c error.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://github.com/ImageMagick/ImageMagick/commit/d4fc44b58a14f76b1ac997517d742ee12c9dc5d3
- https://github.com/ImageMagick/ImageMagick/issues/1611
