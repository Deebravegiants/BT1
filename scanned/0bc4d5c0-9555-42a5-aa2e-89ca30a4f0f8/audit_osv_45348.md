# [M] ImageMagick before 7.1.2-18 contains a memory leak vulnerability in the META reader when...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1047
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1047
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-18 contains a memory leak vulnerability in the META reader when processing APP1JPEG input paths. Attackers can trigger this memory leak by providing specially crafted APP1JPEG image files, causing denial of service through resource exhaustion.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-9r56-3gjq-hqf7
- https://github.com/advisories/GHSA-377p-xr9w-8773
- https://nvd.nist.gov/vuln/detail/CVE-2026-56366
- https://www.vulncheck.com/advisories/imagemagick-memory-leak-in-meta-reader-app1jpeg-error-path
