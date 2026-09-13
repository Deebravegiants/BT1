# [C] JLSEC-2026-824

## Summary
Severity: Critical
Advisory: JLSEC-2026-824
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-824
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
In ImageMagick before 7.0.8-8, a NULL pointer dereference exists in the GetMagickProperty function in `MagickCore/property.c`.

## References
- https://github.com/ImageMagick/ImageMagick/issues/1225
- https://github.com/ImageMagick/ImageMagick/issues/1225
