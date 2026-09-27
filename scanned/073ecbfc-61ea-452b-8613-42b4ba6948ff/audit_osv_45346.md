# [M] ImageMagick before 7.1.2-15 contains a heap-buffer-overflow read vulnerability in GetPixelIndex...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1043
Ecosystem: Julia
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1043
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 contains a heap-buffer-overflow read vulnerability in GetPixelIndex caused by OpenPixelCache updating image channel metadata before pixel cache memory allocation. Attackers can trigger memory and disk allocation failures to cause a heap-buffer-overflow read affecting any writer calling GetPixelIndex.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-gq5v-qf8q-fp77
- https://github.com/advisories/GHSA-m366-rhm3-cx89
- https://nvd.nist.gov/vuln/detail/CVE-2026-56362
- https://www.vulncheck.com/advisories/imagemagick-heap-buffer-overflow-read-in-getpixelindex-via-openpixelcache-metadata-desynchronization
