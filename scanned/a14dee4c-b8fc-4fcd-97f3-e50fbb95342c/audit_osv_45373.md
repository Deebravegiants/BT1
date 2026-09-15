# [H] JLSEC-2026-1095

## Summary
Severity: High
Advisory: JLSEC-2026-1095
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1095
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.19.0 through 1.21.2, a crafted HEIF file (uncompressed `unci` codec, tiled, component-interleaved, 4:2:0) triggers a heap out-of-bounds write in libheif's uncompressed tile decoder. The write overwrites the C++ vtable pointer of an adjacent `unc_decoder_component_interleave` object; the next virtual call dispatches to an attacker-chosen address. Version 1.22.0 patches the issue.

## References
- https://github.com/strukturag/libheif/security/advisories/GHSA-5x55-x5pf-9c6g
