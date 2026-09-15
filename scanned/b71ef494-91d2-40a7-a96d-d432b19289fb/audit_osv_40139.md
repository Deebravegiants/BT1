# [H] libheif: unbounded heap allocation in HEIF sequence parser (stsz fixed-size mode missing bound check)

## Summary
Severity: High
Advisory: CVE-2026-50142
Aliases: GHSA-jvmp-j3cw-84mh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50142
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. From 1.19.0 until 1.23.0, a crafted HEIF sequence accepted by heif_context_read_from_memory() with the msf1 sequence brand can cause unbounded heap allocation. In libheif/sequences/seq_boxes.cc, Box_stsz::parse() applies max_sequence_frames only to variable-size samples, so fixed-size mode accepts an attacker-controlled sample_count without a bound. In libheif/sequences/track.cc, Track::load() also adds current_sample_idx and samples_per_chunk in 32-bit arithmetic, allowing the consistency check to be bypassed by wraparound. The resulting values reach the Chunk::Chunk() allocation path, which can consume gigabytes of memory and crash or stall the process through memory exhaustion. This issue is fixed in version 1.23.0.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.23.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50142.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-jvmp-j3cw-84mh
- https://nvd.nist.gov/vuln/detail/CVE-2026-50142
- https://github.com/strukturag/libheif/commit/a6caa38f7a70d66dc9caec2a7bfe20935b32c622
