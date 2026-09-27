# [H] JLSEC-2026-156

## Summary
Severity: High
Advisory: JLSEC-2026-156
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/JLSEC-2026-156
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.21.2000+0

## Details
libheif is an HEIF and AVIF file format decoder and encoder. Prior to version 1.21.0, a crafted HEIF that exercises the overlay image item path triggers a heap buffer over-read in `HeifPixelImage::overlay()`. The function computes a negative row length (likely from an unclipped overlay rectangle or invalid offsets), which then underflows when converted to `size_t` and is passed to `memcpy`, causing a very large read past the end of the source plane and a crash. Version 1.21.0 contains a patch. As a workaround, avoid decoding images using `iovl` overlay boxes.

## References
- https://github.com/strukturag/libheif/commit/b8c12a7b70f46c9516711a988483bed377b78d46
- https://github.com/strukturag/libheif/releases/tag/v1.21.0
- https://github.com/strukturag/libheif/security/advisories/GHSA-j87x-4gmq-cqfq
