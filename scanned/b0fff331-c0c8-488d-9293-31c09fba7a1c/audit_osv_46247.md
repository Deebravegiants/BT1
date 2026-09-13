# [M] JLSEC-2026-879

## Summary
Severity: Medium
Advisory: JLSEC-2026-879
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-879
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
A flaw was found in ImageMagick in `coders/jp2.c`. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of math division by zero. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1928952
- https://bugzilla.redhat.com/show_bug.cgi?id=1928952
- https://github.com/ImageMagick/ImageMagick/pull/3177
- https://github.com/ImageMagick/ImageMagick/pull/3177
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
