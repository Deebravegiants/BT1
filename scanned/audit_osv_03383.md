# [H] ALPINE-CVE-2025-68431

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-68431
Ecosystem: Alpine:v3.23
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68431
Type: osv

## Affected
- Alpine:v3.23: `libheif` — affected >=0 <1.21.2-r0

## Details
libheif is an HEIF and AVIF file format decoder and encoder. Prior to version 1.21.0, a crafted HEIF that exercises the overlay image item path triggers a heap buffer over-read in `HeifPixelImage::overlay()`. The function computes a negative row length (likely from an unclipped overlay rectangle or invalid offsets), which then underflows when converted to `size_t` and is passed to `memcpy`, causing a very large read past the end of the source plane and a crash. Version 1.21.0 contains a patch. As a workaround, avoid decoding images using `iovl` overlay boxes.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68431
