# [C] FFmpeg versions 8.0 through 8.1.2 contains a stack buffer overflow vulnerability in the Vulkan...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1173
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1173
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=8.0.0+0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=8.1.2+0 <9.0.0+0

## Details
FFmpeg versions 8.0 through 8.1.2 contains a stack buffer overflow vulnerability in the Vulkan HEVC hardware decoder that allows remote attackers to overwrite return addresses and adjacent stack frames by supplying a crafted `HEVC/H.265` bitstream. Attackers can embed a malicious `vps_num_hrd_parameters` value exceeding `HEVC_MAX_SUB_LAYERS` in any supported container format to overflow stack-allocated arrays in the `vk_hevc_end_frame` function, potentially achieving arbitrary code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/92737390dc133daadce47dd7d2ec8ef3d9ebcbed
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23665
- https://github.com/advisories/GHSA-mqq7-j9mq-9jwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-64831
- https://www.vulncheck.com/advisories/ffmpeg-stack-buffer-overflow-in-vulkan-hevc-decoder
