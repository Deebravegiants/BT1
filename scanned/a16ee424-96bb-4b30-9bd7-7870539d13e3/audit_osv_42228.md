# [C] FFmpeg 3.0 - 8.1.2 vf_swaprect Out-of-Bounds Write via NV12 Frame Processing

## Summary
Severity: Critical
Advisory: CVE-2026-65706
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65706
Type: osv

## Details
FFmpeg versions 3.0 through 8.1.2 contain an out-of-bounds write vulnerability in the vf_swaprect video filter that allows attackers to corrupt heap memory by supplying a crafted NV12 video frame with odd width dimensions. The filter_frame() function reuses a temporary row buffer sized for plane 0's single-byte pixel step across all planes, causing an 18-byte memcpy into a 17-byte heap allocation when processing the two-byte-per-sample interleaved chroma plane of a 17x16 NV12 frame, resulting in heap corruption and process crash with potential for code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65706.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65706
- https://www.vulncheck.com/advisories/ffmpeg-vf-swaprect-out-of-bounds-write-via-nv12-frame-processing
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23779
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/a7e38b617b32f996beaa371bbf04b39907d7a527
