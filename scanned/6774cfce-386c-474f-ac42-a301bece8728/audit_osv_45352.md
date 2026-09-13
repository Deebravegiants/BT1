# [M] ImageMagick before 7.1.2-15 and 6.9.13-40 contains a memory leak in coders/txt.c when processing...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1052
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1052
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 and 6.9.13-40 contains a memory leak in `coders/txt.c` when processing TXT files with texture attributes: the texture object allocated via ReadImage is not released when GetTypeMetrics fails, leaking memory each time a crafted TXT file with a texture attribute is processed.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-3q5f-gmjc-38r8
- https://github.com/advisories/GHSA-98gv-6gmj-cm6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-56371
- https://www.vulncheck.com/advisories/imagemagick-memory-leak-in-txt-file-processing-via-texture-attribute
