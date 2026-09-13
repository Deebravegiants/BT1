# [C] FFmpeg versions from 0.5 up to, but not including, 9.0 contain a signed integer overflow...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1188
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1188
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg versions from 0.5 up to, but not including, 9.0 contain a signed integer overflow vulnerability in the DVB subtitle parser in `libavcodec/dvbsub_parser.c` that allows attackers to trigger a heap buffer overflow by supplying a crafted WTV file. The overflow causes the bounds-check guard expression to wrap to `INT_MIN`, bypassing the `PARSE_BUF_SIZE` comparison and invoking memcpy() with attacker-controlled data into a heap buffer, resulting in an out-of-bounds heap write and potential memory corruption or code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/02fc47e13f903768b75f7985a2706a6223ab4506
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/93f2a525ec6c7b467bae68322720d10188fc6e30
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/c6ec28b18cd1eb7d39e6163137367f2d1c62aa7c
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23897
- https://github.com/advisories/GHSA-qw9h-2hhv-hpfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-70628
- https://www.vulncheck.com/advisories/ffmpeg-dvb-subtitle-parser-heap-buffer-overflow-via-wtv-file
