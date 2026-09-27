# [H] JLSEC-2026-884

## Summary
Severity: High
Advisory: JLSEC-2026-884
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-884
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
A flaw was found in ImageMagick in versions before 7.0.11 and before 6.9.12, where a division by zero in WaveImage() of `MagickCore/visual-effects.c` may trigger undefined behavior via a crafted image file submitted to an application using ImageMagick. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1946722
- https://bugzilla.redhat.com/show_bug.cgi?id=1946722
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
