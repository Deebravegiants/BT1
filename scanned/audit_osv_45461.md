# [H] JLSEC-2026-1193

## Summary
Severity: High
Advisory: JLSEC-2026-1193
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1193
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions 1.19.0 through 1.21.2 have a heap OOB read in `ImageItem_Grid::decode_grid_tile` via irot-induced tile-coordinate underflow. Version 1.22.0 fixes the issue.

## References
- https://github.com/strukturag/libheif/commit/e523ec0bf379110b7c33d4c159f8b1202d332157
- https://github.com/strukturag/libheif/security/advisories/GHSA-6x5f-qchq-cxqv
