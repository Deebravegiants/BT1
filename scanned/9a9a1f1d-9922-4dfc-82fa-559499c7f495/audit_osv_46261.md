# [H] JLSEC-2026-892

## Summary
Severity: High
Advisory: JLSEC-2026-892
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-892
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A heap-based-buffer-over-read flaw was found in ImageMagick's GetPixelAlpha() function of 'pixel-accessor.h'. This vulnerability is triggered when an attacker passes a specially crafted Tagged Image File Format (TIFF) image to convert it into a PICON file format. This issue can potentially lead to a denial of service and information disclosure.

## References
- https://access.redhat.com/security/cve/CVE-2022-0284
- https://access.redhat.com/security/cve/CVE-2022-0284
- https://bugzilla.redhat.com/show_bug.cgi?id=2045943
- https://bugzilla.redhat.com/show_bug.cgi?id=2045943
- https://github.com/ImageMagick/ImageMagick/commit/e50f19fd73c792ebe912df8ab83aa51a243a3da7
- https://github.com/ImageMagick/ImageMagick/commit/e50f19fd73c792ebe912df8ab83aa51a243a3da7
- https://github.com/ImageMagick/ImageMagick/issues/4729
- https://github.com/ImageMagick/ImageMagick/issues/4729
