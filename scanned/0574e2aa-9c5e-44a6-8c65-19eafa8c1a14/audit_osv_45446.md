# [C] FFmpeg versions 4.4 through 8.1.2 contain an out-of-bounds memory access vulnerability in the ADX...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1177
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1177
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=4.4.4+0 <9.0.0+0

## Details
FFmpeg versions 4.4 through 8.1.2 contain an out-of-bounds memory access vulnerability in the ADX audio decoder within `libavcodec/adxdec.c` that allows attackers to trigger both out-of-bounds reads and writes by supplying a crafted ADX or AAX audio file with a mid-stream channel layout change. When `AV_PKT_DATA_NEW_EXTRADATA` side data is received mid-stream, the `adx_decode_frame` function re-parses the stream header but fails to update the internal channel state, causing subsequent decoding operations to access the prev[] state array using a stale channel count.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/1836ef96846937a6cc2443698a693104f5c0b21e
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23659
- https://github.com/advisories/GHSA-p2v8-4c4f-rwpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-64835
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-memory-access-in-adx-audio-decoder
