# [H] JLSEC-2026-838

## Summary
Severity: High
Advisory: JLSEC-2026-838
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-838
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
In ImageMagick before 7.0.8-25 and GraphicsMagick through 1.3.31, several memory leaks exist in WritePDFImage in `coders/pdf.c`.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/11ad3aeb8ab1
- http://hg.graphicsmagick.org/hg/GraphicsMagick/rev/11ad3aeb8ab1
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://www.securityfocus.com/bid/106847
- http://www.securityfocus.com/bid/106847
- https://github.com/ImageMagick/ImageMagick/commit/306c1f0fa5754ca78efd16ab752f0e981d4f6b82
- https://github.com/ImageMagick/ImageMagick/commit/306c1f0fa5754ca78efd16ab752f0e981d4f6b82
- https://github.com/ImageMagick/ImageMagick/issues/1454
- https://github.com/ImageMagick/ImageMagick/issues/1454
- https://usn.ubuntu.com/4034-1/
- https://usn.ubuntu.com/4034-1/
- https://www.debian.org/security/2020/dsa-4712
- https://www.debian.org/security/2020/dsa-4712
