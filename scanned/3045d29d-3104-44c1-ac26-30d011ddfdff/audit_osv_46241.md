# [H] JLSEC-2026-864

## Summary
Severity: High
Advisory: JLSEC-2026-864
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-864
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
A flaw was found in ImageMagick in `MagickCore/statistic.c`. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of values outside the range of type `unsigned long`. This would most likely lead to an impact to application availability, but could potentially cause other problems related to undefined behavior. This flaw affects ImageMagick versions prior to 7.0.8-69.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894686
- https://bugzilla.redhat.com/show_bug.cgi?id=1894686
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
