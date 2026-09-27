# [M] JLSEC-2026-1098

## Summary
Severity: Medium
Advisory: JLSEC-2026-1098
Ecosystem: Julia
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1098
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Prior to version 1.22.0, `Track::init_sample_timing_table()` in `libheif/sequences/track.cc` stores an out-of-bounds chunk index (`m_chunks.size()`) into `m_presentation_timeline` when the number of chunks defined in the `stco` box is less than the number of samples in `stsz`. A subsequent call to `heif_track_get_next_raw_sequence_sample()` reads `m_chunks[chunk_idx]` with that OOB index, causing a heap-buffer-overflow. Version 1.22.0 fixes the issue.

## References
- https://github.com/strukturag/libheif/security/advisories/GHSA-wqjg-4x9g-6cvg
