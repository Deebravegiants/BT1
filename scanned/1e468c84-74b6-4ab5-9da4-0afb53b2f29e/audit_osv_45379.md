# [M] JLSEC-2026-1101

## Summary
Severity: Medium
Advisory: JLSEC-2026-1101
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1101
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Prior to version 1.22.1, the uncompressed HEIF decoder validates explicit icef compressed-unit offsets using `unit_offset` + `unit_size`. Because the addition can wrap, a crafted HEIF file can pass the range check and then construct a vector from iterators outside the compressed item buffer, producing an out-of-bounds heap read and crash. Version 1.22.1 patches the issue.

## References
- https://github.com/strukturag/libheif/security/advisories/GHSA-r7qj-cg5r-r6vf
