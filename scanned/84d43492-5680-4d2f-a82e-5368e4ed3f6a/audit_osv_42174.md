# [C] FFmpeg 8.0 - 8.1.2 Stack Buffer Overflow in Vulkan HEVC Decoder

## Summary
Severity: Critical
Advisory: CVE-2026-64831
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-64831
Type: osv

## Details
FFmpeg versions 8.0 through 8.1.2 contains a stack buffer overflow vulnerability in the Vulkan HEVC hardware decoder that allows remote attackers to overwrite return addresses and adjacent stack frames by supplying a crafted HEVC/H.265 bitstream. Attackers can embed a malicious vps_num_hrd_parameters value exceeding HEVC_MAX_SUB_LAYERS in any supported container format to overflow stack-allocated arrays in the vk_hevc_end_frame function, potentially achieving arbitrary code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64831.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64831
- https://www.vulncheck.com/advisories/ffmpeg-stack-buffer-overflow-in-vulkan-hevc-decoder
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23665
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/92737390dc133daadce47dd7d2ec8ef3d9ebcbed
