# [H] ImageMagick before 7.1.2-19 contains a heap buffer overflow vulnerability in the FTXT encoder due...

## Summary
Severity: High
Advisory: JLSEC-2026-1055
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1055
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-19 contains a heap buffer overflow vulnerability in the FTXT encoder due to missing boundary checks when parsing ftxt:format. Remote attackers can trigger an out of bounds read by crafting malicious FTXT image files to cause denial of service or information disclosure.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-w54j-7wpm-crhj
- https://github.com/advisories/GHSA-g4x5-mww6-m42x
- https://nvd.nist.gov/vuln/detail/CVE-2026-56374
- https://www.vulncheck.com/advisories/imagemagick-heap-buffer-overflow-in-ftxt-encoder-via-format-parameter
