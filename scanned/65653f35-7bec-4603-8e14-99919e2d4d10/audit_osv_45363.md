# [H] ImageMagick before 7.1.2-26 contains a memory leak vulnerability in the JNG encoder when a blob...

## Summary
Severity: High
Advisory: JLSEC-2026-1072
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1072
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick before 7.1.2-26 contains a memory leak vulnerability in the JNG encoder when a blob cannot be opened. Attackers can trigger the memory leak by providing malformed JNG files that fail blob operations, causing resource exhaustion.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-99w9-hv66-rfv7
- https://github.com/advisories/GHSA-848j-9x6v-4m2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-61866
- https://www.vulncheck.com/advisories/imagemagick-before-26-memory-leak-in-jng-encoder
