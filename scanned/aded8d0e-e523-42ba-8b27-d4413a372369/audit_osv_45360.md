# [H] ImageMagick before 7.1.2-26 contains a heap use-after-free vulnerability caused by missing null...

## Summary
Severity: High
Advisory: JLSEC-2026-1063
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1063
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick before 7.1.2-26 contains a heap use-after-free vulnerability caused by missing null check when parsing XMP profiles. Attackers can craft malicious image files with specially crafted XMP data to trigger the vulnerability and cause application crashes.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qh5g-q395-cx4j
- https://github.com/advisories/GHSA-84mh-5fq7-7fx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-61857
- https://www.vulncheck.com/advisories/imagemagick-before-26-heap-use-after-free-via-xmp
