# [M] FFmpeg versions from 3.0 up to, but not including, 9.0 contain an uninitialized heap memory read...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1189
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1189
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg versions from 3.0 up to, but not including, 9.0 contain an uninitialized heap memory read vulnerability in the native RSCC decoder (`libavcodec/rscc.c`) that allows attackers to disclose heap memory contents by supplying a crafted video file with a compressed tile that decompresses fewer bytes than the declared tile geometry requires. When `rscc_decode_frame()` calls `av_image_copy_plane()` without validating the decompressed byte count against the tile dimensions, the unwritten suffix of the persistent intermediate buffer ctx->`inflated_buf` is copied into the decoded frame, potentially exposing data from prior heap allocations or previous decoded frames in persistent decoding services.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/533a6198505edd1379e1cd722852350ae4a85acc
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/a5fe21a1a410a680fe93c33b0dd696b7e1c3aea4
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/cd1f545cf27ba08f6f5b31b1e92665d7874d4fd7
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23895
- https://github.com/advisories/GHSA-824f-v6qw-342h
- https://nvd.nist.gov/vuln/detail/CVE-2026-70629
- https://www.vulncheck.com/advisories/ffmpeg-uninitialized-heap-memory-read-in-rscc-decoder
