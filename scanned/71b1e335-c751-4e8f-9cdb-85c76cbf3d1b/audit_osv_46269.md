# [H] JLSEC-2026-900

## Summary
Severity: High
Advisory: JLSEC-2026-900
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-900
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+3

## Details
In ImageMagick, there is load of misaligned address for type 'double', which requires 8 byte alignment and for type 'float', which requires 4 byte alignment at `MagickCore/property.c`. Whenever crafted or untrusted input is processed by ImageMagick, this causes a negative impact to application availability or other problems related to undefined behavior.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2091813
- https://bugzilla.redhat.com/show_bug.cgi?id=2091813
- https://github.com/ImageMagick/ImageMagick/commit/eac8ce4d873f28bb6a46aa3a662fb196b49b95d0
- https://github.com/ImageMagick/ImageMagick/commit/eac8ce4d873f28bb6a46aa3a662fb196b49b95d0
- https://github.com/ImageMagick/ImageMagick6/commit/dc070da861a015d3c97488fdcca6063b44d47a7b
- https://github.com/ImageMagick/ImageMagick6/commit/dc070da861a015d3c97488fdcca6063b44d47a7b
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
