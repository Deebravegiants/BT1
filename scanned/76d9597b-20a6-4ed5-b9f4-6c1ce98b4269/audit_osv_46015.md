# [M] JLSEC-2026-573

## Summary
Severity: Medium
Advisory: JLSEC-2026-573
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/JLSEC-2026-573
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.21.2 and prior, a malformed HEIF sequence file can trigger an out-of-bounds read in core sequence parsing logic, causing DoS. A malformed file can have `stco.entry_count` == 0 (creating no chunks) while still passing validation because `saio.entry_count` == 0 matches, but with `saiz.sample_count` > 0 the SampleAuxInfoReader constructor still enters its loop. This leads to an out-of-bounds dereference on the empty chunks[0] in chunked mode.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://github.com/strukturag/libheif/security/advisories/GHSA-p82x-fpmv-576r
