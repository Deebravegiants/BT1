# [M] JLSEC-2026-1100

## Summary
Severity: Medium
Advisory: JLSEC-2026-1100
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1100
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.21.2 and prior, the inline mask parsing code in `libheif/region.cc` contains an integer overflow. Both `width` and `height` are `unsigned int` (32-bit) values parsed from the HEIF file. Their product can exceed `UINT32_MAX`, wrapping to a small value before the division by 8. This causes an undersized buffer allocation, leading to out-of-bounds memory access when the mask data is later interpreted as a `width x height` bitmap. Version 1.22.0 patches the issue.

## References
- https://github.com/strukturag/libheif/security/advisories/GHSA-h4wm-6wwf-qvhx
