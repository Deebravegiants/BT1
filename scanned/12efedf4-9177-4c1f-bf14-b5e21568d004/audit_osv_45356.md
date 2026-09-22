# [H] ImageMagick before 7.1.2-15 (and 6.x before 6.9.13-40) contains a heap out-of-bounds read in the...

## Summary
Severity: High
Advisory: JLSEC-2026-1059
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1059
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=7.1.2001+0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 (and 6.x before 6.9.13-40) contains a heap out-of-bounds read in the PCD coder's DecodeImage loop. A crafted PCD file can trigger a one-byte heap out-of-bounds read during image decoding, resulting in denial of service and potential disclosure of an adjacent heap byte.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wgxp-q8xq-wpp9
- https://github.com/advisories/GHSA-jmqv-2mx7-544h
- https://nvd.nist.gov/vuln/detail/CVE-2026-56378
- https://www.vulncheck.com/advisories/imagemagick-heap-out-of-bounds-read-in-pcd-decoder
