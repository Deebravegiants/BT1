# [C] FFmpeg versions 3.0 through 8.1.2 contain an out-of-bounds write vulnerability in the vf_swaprect...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1181
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1181
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg versions 3.0 through 8.1.2 contain an out-of-bounds write vulnerability in the `vf_swaprect` video filter that allows attackers to corrupt heap memory by supplying a crafted NV12 video frame with odd width dimensions. The `filter_frame()` function reuses a temporary row buffer sized for plane 0's single-byte pixel step across all planes, causing an 18-byte memcpy into a 17-byte heap allocation when processing the two-byte-per-sample interleaved chroma plane of a 17x16 NV12 frame, resulting in heap corruption and process crash with potential for code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/a7e38b617b32f996beaa371bbf04b39907d7a527
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23779
- https://github.com/advisories/GHSA-g9rh-4g64-7qxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-65706
- https://www.vulncheck.com/advisories/ffmpeg-vf-swaprect-out-of-bounds-write-via-nv12-frame-processing
