# [H] ImageMagick before 7.1.2-19 contains an off-by-one error in morphology validation allowing out-of...

## Summary
Severity: High
Advisory: JLSEC-2026-1042
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1042
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-19 contains an off-by-one error in morphology validation allowing out-of-bounds heap buffer reads. Attackers can trigger heap buffer overflow by providing incorrect morphology parameters causing single pixel memory access violations.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-q8h3-jv9v-57qx
- https://github.com/advisories/GHSA-4h5w-9gq6-38f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-56361
- https://www.vulncheck.com/advisories/imagemagick-heap-buffer-overflow-via-off-by-one-in-morphology-processing
