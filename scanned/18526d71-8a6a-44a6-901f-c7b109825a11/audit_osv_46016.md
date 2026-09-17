# [H] JLSEC-2026-574

## Summary
Severity: High
Advisory: JLSEC-2026-574
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/JLSEC-2026-574
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.21.2 and prior, a crafted HEIF sequence file where the saiz box declares more samples than actually exist in the track's chunk table causes a heap-buffer-overflow (out-of-bounds read) in the SampleAuxInfoReader constructor. The SampleAuxInfoReader constructor iterates over `saiz->get_num_samples()` samples but doesn't validate that this count is consistent with the number of chunks in the chunks vector. When saiz declares more samples than the chunks cover, the loop increments `current_chunk` past chunks.size(), causing an out-of-bounds read on the chunks vector. The vulnerability is triggered during file parsing (`heif_context_read_from_file`) without any additional user interaction. Any application using libheif to open untrusted HEIF files is affected. This issue has been fixed in version 1.22.0.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://github.com/strukturag/libheif/security/advisories/GHSA-xj92-xjff-h8w3
