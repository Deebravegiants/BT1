# [C] ImageMagick before 7.1.2-19 contains a heap buffer overflow vulnerability in the magnify...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1053
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1053
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-19 contains a heap buffer overflow vulnerability in the magnify operation that allows attackers to read out of bounds memory. An unrecognized magnify:method value triggers an out of bounds read, potentially exposing sensitive information or causing denial of service.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8vfj-q2cp-5m5j
- https://github.com/advisories/GHSA-x98x-mp75-v6m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56372
- https://www.vulncheck.com/advisories/imagemagick-heap-buffer-overflow-read-via-unrecognized-magnify-method
