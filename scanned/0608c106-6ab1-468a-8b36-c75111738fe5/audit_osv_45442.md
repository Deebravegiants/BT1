# [C] FFmpeg versions 2.1 through 8.1.2 contains a heap buffer overflow vulnerability in the VobSub...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1172
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1172
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg versions 2.1 through 8.1.2 contains a heap buffer overflow vulnerability in the VobSub subtitle demuxer that allows attackers to corrupt adjacent heap memory by supplying a malicious .sub/.idx subtitle file declaring more distinct stream IDs than the fixed-size array bounds in `libavformat/mpeg.c`. Attackers can craft a subtitle file with excessive distinct stream IDs to trigger unbounded writes beyond the vobsub->q[] array boundary via `ff_subtitles_queue_insert()`, potentially achieving arbitrary code execution in any application using FFmpeg's VobSub demuxer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/dbd495f066a85ba96b17433f4306582aa37c3951
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23657
- https://github.com/advisories/GHSA-jphx-q7f7-4x8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-64830
- https://www.vulncheck.com/advisories/ffmpeg-heap-buffer-overflow-via-vobsub-subtitle-demuxer
