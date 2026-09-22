# [M] JLSEC-2026-880

## Summary
Severity: Medium
Advisory: JLSEC-2026-880
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-880
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in ImageMagick in `MagickCore/resize.c`. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of math division by zero. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1928958
- https://bugzilla.redhat.com/show_bug.cgi?id=1928958
- https://github.com/ImageMagick/ImageMagick/pull/3193
- https://github.com/ImageMagick/ImageMagick/pull/3193
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
