# [C] FFmpeg versions 4.4 through 8.1.2 contain a double-free vulnerability in the NVIDIA NVDEC...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1174
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1174
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=4.4.4+0 <9.0.0+0

## Details
FFmpeg versions 4.4 through 8.1.2 contain a double-free vulnerability in the NVIDIA NVDEC hardware decoder within `libavcodec/nvdec.c` that allows attackers to trigger memory corruption by supplying a crafted video file. When no decoder surfaces remain, the `ff_nvdec_start_frame_sep_ref` error path frees memory via `nvdec_fdd_priv_free` while the calling layer subsequently frees the same frame description data, resulting in a double-free of the underlying decoder context in any FFmpeg-based application using NVDEC hardware-accelerated decoding.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/4c6217477fc64305055b37d9d1d0d76d30e37f97
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23664
- https://github.com/advisories/GHSA-jc8j-9799-c943
- https://nvd.nist.gov/vuln/detail/CVE-2026-64832
- https://www.vulncheck.com/advisories/ffmpeg-double-free-in-nvdec-hardware-decoder-via-nvdec-c
