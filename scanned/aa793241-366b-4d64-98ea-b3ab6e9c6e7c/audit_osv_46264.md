# [M] JLSEC-2026-895

## Summary
Severity: Medium
Advisory: JLSEC-2026-895
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-895
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
In ImageMagick, a crafted file could trigger an assertion failure when a call to WriteImages was made in `MagickWand/operation.c`, due to a NULL image list. This could potentially cause a denial of service. This was fixed in upstream ImageMagick version 7.1.0-30.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2116537
- https://bugzilla.redhat.com/show_bug.cgi?id=2116537
