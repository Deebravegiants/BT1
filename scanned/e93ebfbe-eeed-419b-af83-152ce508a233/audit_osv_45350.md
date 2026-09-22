# [H] JLSEC-2026-1049

## Summary
Severity: High
Advisory: JLSEC-2026-1049
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1049
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 contains a memory leak vulnerability in multiple coders that write raw pixel data where allocated objects are not properly freed. Attackers can trigger this leak by processing specially crafted images, causing memory exhaustion and denial of service.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wfx3-6g53-9fgc
- https://www.vulncheck.com/advisories/imagemagick-memory-leak-in-raw-pixel-data-coders
