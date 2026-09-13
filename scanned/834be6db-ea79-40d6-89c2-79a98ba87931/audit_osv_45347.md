# [M] ImageMagick before 7.1.2-19 contains a memory leak vulnerability in the PNG encoder when writing...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1046
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1046
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-19 contains a memory leak vulnerability in the PNG encoder when writing MNG images. Attackers can trigger the encoder failure condition to exhaust memory resources and cause denial of service.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-x928-4434-crqj
- https://github.com/advisories/GHSA-hq73-7c65-p9cq
- https://nvd.nist.gov/vuln/detail/CVE-2026-56365
- https://www.vulncheck.com/advisories/imagemagick-memory-leak-in-png-encoder-via-mng-image-writing
