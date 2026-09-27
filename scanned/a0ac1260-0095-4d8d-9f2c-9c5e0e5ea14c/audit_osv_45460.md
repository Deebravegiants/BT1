# [C] FFmpeg versions from 4.4 up to, but not including, 9.0 contain an out-of-bounds heap write...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1192
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1192
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=4.4.4+0 <9.0.0+0

## Details
FFmpeg versions from 4.4 up to, but not including, 9.0 contain an out-of-bounds heap write vulnerability in the native GoPro CineForm HD (CFHD) decoder that allows remote attackers to corrupt heap memory by supplying a crafted AVI file during stream probing. The `cfhd_decode()` function fails to enforce the non-Bayer logical output-width invariant in the transform-type-2 reconstruction path, causing `horiz_filter_clip()` to write oversized 16-bit sample rows far beyond the allocated output frame buffer, which can be escalated to arbitrary code execution via overwrite of a live cleanup callback pointer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/1006a2151236f9235bf02822f263b3fb0532111e
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/16b2049d4d5222db6cd7c031409058571c94f6a9
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/db05df9d135fb56a4babb836d5e9f5c1d984e087
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23898
- https://github.com/advisories/GHSA-q24x-99v6-6hxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-70632
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-in-cfhd-decoder-via-avi-demuxing
