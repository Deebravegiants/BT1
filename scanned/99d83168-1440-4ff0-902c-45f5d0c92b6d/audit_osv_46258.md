# [M] JLSEC-2026-889

## Summary
Severity: Medium
Advisory: JLSEC-2026-889
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-889
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A NULL pointer dereference flaw was found in ImageMagick in versions prior to 7.0.10-31 in ReadSVGImage() in `coders/svg.c`. This issue is due to not checking the return value from libxml2's xmlCreatePushParserCtxt() and uses the value directly, which leads to a crash and segmentation fault.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1970569
- https://bugzilla.redhat.com/show_bug.cgi?id=1970569
- https://github.com/ImageMagick/ImageMagick/issues/2624
- https://github.com/ImageMagick/ImageMagick/issues/2624
- https://lists.debian.org/debian-lts-announce/2022/05/msg00018.html
- https://lists.debian.org/debian-lts-announce/2022/05/msg00018.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
