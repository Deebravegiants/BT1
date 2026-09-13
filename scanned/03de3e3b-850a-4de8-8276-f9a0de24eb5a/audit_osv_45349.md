# [C] ImageMagick before 7.1.2-15 and 6.9.x before 6.9.13-40 contains an integer overflow in the PSB ...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1048
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1048
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=7.1.2001+0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 and 6.9.x before 6.9.13-40 contains an integer overflow in the PSB (PSD v2) RLE decoding path (ReadPSDChannelRLE in `coders/psd.c`) that causes a heap out-of-bounds read on 32-bit builds. Processing a crafted PSB file can lead to information disclosure or a crash.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-273h-m46v-96q4
- https://github.com/advisories/GHSA-rg39-4fm5-hrp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-56367
- https://www.vulncheck.com/advisories/imagemagick-heap-out-of-bounds-read-in-psb-rle-decoding
