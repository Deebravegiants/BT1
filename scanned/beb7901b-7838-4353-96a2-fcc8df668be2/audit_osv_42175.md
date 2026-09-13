# [C] FFmpeg 4.4 - 8.1.2 Double-Free in NVDEC Hardware Decoder via nvdec.c

## Summary
Severity: Critical
Advisory: CVE-2026-64832
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-64832
Type: osv

## Details
FFmpeg versions 4.4 through 8.1.2 contain a double-free vulnerability in the NVIDIA NVDEC hardware decoder within libavcodec/nvdec.c that allows attackers to trigger memory corruption by supplying a crafted video file. When no decoder surfaces remain, the ff_nvdec_start_frame_sep_ref error path frees memory via nvdec_fdd_priv_free while the calling layer subsequently frees the same frame description data, resulting in a double-free of the underlying decoder context in any FFmpeg-based application using NVDEC hardware-accelerated decoding.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64832.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64832
- https://www.vulncheck.com/advisories/ffmpeg-double-free-in-nvdec-hardware-decoder-via-nvdec-c
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23664
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/4c6217477fc64305055b37d9d1d0d76d30e37f97
